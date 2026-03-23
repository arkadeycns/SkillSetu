from core.database import get_db

async def get_national_stats():
    db = get_db()
    
    # 1. Total Workers (Count all users in the DB)
    total_workers = await db.users.count_documents({})
    
    # 2. Pass Count & Rate (Users with at least one "Verified" skill)
    pass_count = await db.users.count_documents({"skills.status": "Verified"})
    pass_rate = int((pass_count / total_workers) * 100) if total_workers > 0 else 0

    # 3. Skill Distribution for the Pie Chart (Groups and counts all trades)
    skill_pipeline = [
        {"$unwind": "$skills"}, 
        {"$group": {"_id": "$skills.skill_name", "value": {"$sum": 1}}}, 
        {"$project": {"name": "$_id", "value": 1, "_id": 0}}, 
        {"$sort": {"value": -1}}
    ]
    skill_cursor = db.users.aggregate(skill_pipeline)
    skill_data = await skill_cursor.to_list(length=10) 

    # 4. Live Feed (Get the last 10 assessment attempts)
    feed_pipeline = [
        {"$unwind": "$activity_log"},
        {"$sort": {"activity_log.timestamp": -1}},
        {"$limit": 10},
        {"$project": {
            "name": "$activity_log.name",
            "skill": "$activity_log.skill",
            "result": "$activity_log.result",
            "date": "$activity_log.date",
            "_id": 0
        }}
    ]
    feed_cursor = db.users.aggregate(feed_pipeline)
    live_feed = await feed_cursor.to_list(length=10)

    # 5. State Data (For the India Heatmap)
    state_pipeline = [
        {"$match": {"state": {"$exists": True, "$ne": ""}}}, 
        {"$group": {"_id": "$state", "count": {"$sum": 1}}},
        {"$project": {"id": "$_id", "count": 1, "_id": 0}}
    ]
    state_cursor = db.users.aggregate(state_pipeline)
    heatmap_data = await state_cursor.to_list(length=40)

    return {
        "totalWorkers": total_workers,
        "passCount": pass_count,
        "passRate": pass_rate,
        "skillData": skill_data,
        "liveFeed": live_feed,
        "heatmapData": heatmap_data
    }