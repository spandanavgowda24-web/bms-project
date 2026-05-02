# clear_analysis_cache.py
from database import db

# Clear all analysis cache
result = db.analysis.delete_many({})
print(f"✅ Cleared {result.deleted_count} cached analysis results")

# Also update all videos to have video_type = "public"
video_result = db.videos.update_many(
    {},
    {"$set": {"video_type": "public"}}
)
print(f"✅ Updated {video_result.modified_count} videos to public")