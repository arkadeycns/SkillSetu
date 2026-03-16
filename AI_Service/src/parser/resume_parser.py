import re


def extract_email(text):
    match = re.search(r"\S+@\S+", text)
    return match.group(0) if match else None


def extract_phone(text):
    match = re.search(r"\+?\d[\d -]{8,}\d", text)
    return match.group(0) if match else None


def extract_skills(text):

    skill_keywords = [
        "python",
        "machine learning",
        "react",
        "fastapi",
        "sql",
        "docker",
        "node",
        "tensorflow"
    ]

    text_lower = text.lower()

    return [skill for skill in skill_keywords if skill in text_lower]


def parse_resume(text):

    return {
        "name": None,
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": [],
        "experience": []
    }