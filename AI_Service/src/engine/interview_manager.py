"""In-memory session state manager for multi-turn assessments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List
from uuid import uuid4

from src.engine.interview_reporter import generate_final_interview_report
from src.engine.question_bank import QuestionItem, get_category_questions


@dataclass
class TurnRecord:
    stage: str
    question_id: str
    question_text: str
    answer_en: str
    evaluation: Dict[str, Any]


@dataclass
class SessionState:
    session_id: str
    category_id: str
    questions: List[QuestionItem]
    primary_index: int = 0
    stage: str = "primary"  # primary | retry_primary | counter_1 | counter_2 | completed
    current_counters: List[str] = field(default_factory=list)
    retry_used_for_primary: bool = False
    counter_retry_used_for_current: bool = False
    history: List[TurnRecord] = field(default_factory=list)


class InterviewManager:
    def __init__(self) -> None:
        self._sessions: Dict[str, SessionState] = {}

    def start_session(self, category_id: str) -> SessionState:
        questions = get_category_questions(category_id)
        session_id = uuid4().hex
        state = SessionState(session_id=session_id, category_id=category_id, questions=questions)
        self._sessions[session_id] = state
        return state

    def get_session(self, session_id: str) -> SessionState:
        state = self._sessions.get(session_id)
        if not state:
            raise KeyError(f"Session not found: {session_id}")
        return state

    def get_current_prompt(self, state: SessionState) -> Dict[str, Any]:
        if state.stage == "completed":
            return {
                "stage": "completed",
                "question": None,
                "primary_number": 10,
                "total_primaries": len(state.questions),
            }

        primary = state.questions[state.primary_index]
        if state.stage in {"primary", "retry_primary"}:
            return {
                "stage": state.stage,
                "question_id": primary.id if state.stage == "primary" else f"{primary.id}-R1",
                "question": primary.text,
                "primary_number": state.primary_index + 1,
                "total_primaries": len(state.questions),
            }

        counter_idx = 0 if state.stage == "counter_1" else 1
        return {
            "stage": state.stage,
            "question_id": f"{primary.id}-C{counter_idx + 1}",
            "question": state.current_counters[counter_idx],
            "primary_number": state.primary_index + 1,
            "total_primaries": len(state.questions),
        }

    def record_answer(self, state: SessionState, answer_en: str, evaluation: Dict[str, Any]) -> None:
        prompt = self.get_current_prompt(state)
        state.history.append(
            TurnRecord(
                stage=state.stage,
                question_id=str(prompt.get("question_id", "")),
                question_text=str(prompt.get("question", "")),
                answer_en=answer_en,
                evaluation=evaluation,
            )
        )

    def advance_after_primary(self, state: SessionState, counters: List[str]) -> None:
        if counters:
            # Keep only two counters by contract.
            state.current_counters = counters[:2]
            if len(state.current_counters) == 1:
                state.current_counters.append("Can you explain the missing safety step in detail?")
            state.stage = "counter_1"
            state.counter_retry_used_for_current = False
            return
        self._advance_to_next_primary(state)

    def skip_current_primary(self, state: SessionState) -> None:
        """Explicitly skip current primary question and move to next."""
        self._advance_to_next_primary(state)

    def advance_after_unsatisfactory_primary(self, state: SessionState) -> bool:
        """Return True if moved to retry stage, else False when advanced to next primary."""
        if state.stage == "primary" and not state.retry_used_for_primary:
            state.retry_used_for_primary = True
            state.stage = "retry_primary"
            state.current_counters = []
            state.counter_retry_used_for_current = False
            return True

        # Unsatisfactory on retry or any unexpected state in primary track: move on.
        self._advance_to_next_primary(state)
        return False

    def advance_after_counter(self, state: SessionState) -> None:
        if state.stage == "counter_1":
            state.stage = "counter_2"
            state.counter_retry_used_for_current = False
            return
        self._advance_to_next_primary(state)

    def retry_current_counter(self, state: SessionState) -> bool:
        """Retry active counter once; returns True when retry remains in same stage."""
        if state.stage not in {"counter_1", "counter_2"}:
            return False
        if state.counter_retry_used_for_current:
            return False
        state.counter_retry_used_for_current = True
        return True

    def _advance_to_next_primary(self, state: SessionState) -> None:
        state.primary_index += 1
        state.current_counters = []
        state.retry_used_for_primary = False
        state.counter_retry_used_for_current = False
        if state.primary_index >= len(state.questions):
            state.stage = "completed"
        else:
            state.stage = "primary"

    def summarize(self, state: SessionState) -> Dict[str, Any]:
        total_turns = len(state.history)
        passed_turns = sum(1 for turn in state.history if bool(turn.evaluation.get("pass_fail", False)))

        history_payload = [
            {
                "stage": turn.stage,
                "question_id": turn.question_id,
                "question_text": turn.question_text,
                "answer_en": turn.answer_en,
                "evaluation": turn.evaluation,
            }
            for turn in state.history
        ]

        report = generate_final_interview_report(
            category_id=state.category_id,
            history=history_payload,
            total_primaries=len(state.questions),
            completed_primaries=len(
                {
                    turn.question_id.split("-", 1)[0]
                    for turn in state.history
                    if turn.question_id
                }
            ),
        )

        strengths = report.get("strengths", [])
        improvements = report.get("improvements", [])
        return {
            "session_id": state.session_id,
            "category_id": state.category_id,
            "stage": state.stage,
            "primary_progress": min(state.primary_index, len(state.questions)),
            "total_primaries": len(state.questions),
            "total_turns": total_turns,
            "pass_rate": (passed_turns / total_turns) if total_turns else 0.0,
            "overall_score": report.get("overall_score", 0),
            "score": report.get("overall_score", 0),
            "result": report.get("result", "INCOMPLETE"),
            "summary": report.get("summary", ""),
            "feedback": report.get("feedback", ""),
            "strengths": strengths,
            "improvements": improvements,
            "gaps": improvements,
            "history": history_payload,
        }
