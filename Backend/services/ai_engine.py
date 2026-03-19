def generate_training_recommendations(user_data):
    skills = user_data.get("skills", [])
    level = user_data.get("experience_level", "beginner")

    expected_skills = ["Arrays", "Strings", "Graphs", "DP", "OS", "DBMS"]
    weaknesses = [s for s in expected_skills if s not in skills]

    recommendations = []

    for w in weaknesses:
        if w == "Graphs":
            plan = ["BFS", "DFS"] if level == "beginner" else ["Dijkstra", "Topo Sort"]

            recommendations.append({
                "title": "Graphs",
                "priority": "High",
                "plan": plan
            })

        elif w == "DP":
            recommendations.append({
                "title": "Dynamic Programming",
                "priority": "High",
                "plan": ["1D DP", "Knapsack"]
            })

        elif w == "OS":
            recommendations.append({
                "title": "Operating Systems",
                "priority": "Medium",
                "plan": ["Processes", "Scheduling"]
            })

    return {
        "skills": skills,
        "weakness": weaknesses,
        "recommendations": recommendations
    }


def generate_chat_response(message, user_data):
    message = message.lower()
    skills = user_data.get("skills", [])

    if "dsa" in message:
        return f"You know {skills}. Focus next on Graphs and DP."

    elif "backend" in message:
        return "Learn APIs, databases, authentication, and build projects."

    return "Tell me your goal and I will guide you step by step."