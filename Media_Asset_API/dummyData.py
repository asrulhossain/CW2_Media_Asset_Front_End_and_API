import random
import json
from datetime import datetime, timedelta
from bson import ObjectId
from werkzeug.security import generate_password_hash

DEMO_PASSWORD = "Password123!"   
TOTAL = 100                     

def generate_data():
    project_titles = ['Documentary Cut', 'Commercial Spot', 'Podcast Audio', 'Music Video Master', 'Feature Film Polish', 'Travel Vlog', 'Corporate Promo']
    drives = ['RAID_01', 'SSD_Vault_A', 'NAS_Archive', 'Cloud_Cold_Storage', 'Shuttle_Drive_B']
    formats = ['.mp4', '.mov', '.mxf', '.braw', '.r3d', '.wav']
    resolutions = ['1920x1080', '3840x2160', '4096x2160', '8192x4320']
    departments = ['Post-Production', 'Cinematography', 'Sound Design', 'Color Grading', 'VFX Dept']
    actions = ['UPLOADED', 'MODIFIED', 'REVIEWED', 'ARCHIVED', 'EXPORTED']
    task_names = ['Color Grade', 'Audio Sync', 'Noise Reduction', 'Metadata Tagging', 'Proxy Generation']
    regions = ['UK', 'US', 'Global', 'EU']
    statuses = ['In Progress', 'Review', 'Completed']
    tag_pool = {
        'Content': ['B-Roll', 'Interview', 'Drone', 'Studio', 'Raw', 'VFX', 'Audio', 'Timelapse', 'Aerial', 'Close-Up',
                    'Wide Shot', 'Slow Motion', 'Green Screen', 'B-Cam', 'Establishing Shot', 'Behind The Scenes', 'Final Cut', 'Rough Cut',
                    'Color Graded', 'Sound Mix', 'Voiceover', 'Music', 'Archive', 'Stock', 'Logo', 'Title Card', 'Lower Third', 'Transition',
                    'Reaction', 'Montage', 'Dialogue', 'Action', 'Night', 'Day', 'Handheld', 'Tripod', 'Gimbal', 'Underwater', 'Interior', 'Exterior'],
        'Location': ['London', 'Belfast', 'New York', 'Tokyo', 'Paris', 'Dublin', 'Berlin', 'Madrid', 'Rome', 'Sydney',
                     'Toronto', 'Los Angeles', 'Chicago', 'Seoul', 'Mumbai', 'Cairo', 'Lisbon', 'Oslo', 'Prague', 'Vienna'],
        'Language': ['English', 'Spanish', 'French', 'Irish', 'German', 'Italian', 'Japanese', 'Korean', 'Portuguese', 'Arabic',
                     'Hindi', 'Mandarin', 'Dutch', 'Polish', 'Swedish'],
        'Audience': ['Kids', 'Corporate', 'Social Media', 'Broadcast', 'Teens', 'Adults', 'Families', 'Students', 'Investors', 'Customers',
                     'Press', 'Festival', 'Cinema', 'Web', 'Mobile', 'TV', 'Internal', 'Public', 'Premium', 'Educational',
                     'Documentary', 'Advertising', 'Training', 'Event', 'Promo']
    }

    start_date = datetime.now() - timedelta(days=730)

    # TAGS 
    tags = []
    for category, names in tag_pool.items():
        for name in names:
            tags.append({"_id": {"$oid": str(ObjectId())}, "tag_name": name, "category": category})
    assert len(tags) == TOTAL and len({t["tag_name"].lower() for t in tags}) == TOTAL

    # USERS 
    users = []
    password_hash = generate_password_hash(DEMO_PASSWORD)
    for i in range(TOTAL):
        joined_at = start_date + timedelta(days=random.randint(1, 365))
        max_quota = random.choice([250.0, 500.0, 1000.0, 2500.0])
        used_quota = round(random.uniform(10.0, max_quota - 5.0), 2)
        allowed_drives = random.sample(drives, random.randint(1, 3))
        allowed_formats = random.sample(formats, random.randint(3, 5))
        is_admin = i < 3

        recent_activity = []
        for _ in range(random.randint(1, 3)):
            act_date = datetime.now() - timedelta(days=random.randint(1, 30))
            recent_activity.append({
                "action": random.choice(actions),
                "timestamp": act_date.strftime("%Y-%m-%d %H:%M:%S"),
                "metadata": {
                    "target_format": random.choice(allowed_formats),
                    "target_drive": random.choice(allowed_drives)
                }
            })

        users.append({
            "_id": {"$oid": str(ObjectId())},
            "name": f"User {i+1}",
            "email": f"user{i+1}@studio.com",
            "password_hash": password_hash,
            "role": "Admin" if is_admin else "Creator",
            "profile": {
                "department": random.choice(departments),
                "joined_date": joined_at.strftime("%Y-%m-%d"),
                "is_active": True if i < 10 else random.choice([True] * 9 + [False])
            },
            "storage_metrics": {
                "max_quota_gb": max_quota,
                "used_quota_gb": used_quota,
                "quota_warning": (used_quota / max_quota) > 0.85
            },
            "media_permissions": {
                "assigned_drives": allowed_drives,
                "allowed_formats": allowed_formats,
                "max_allowed_resolution": random.choice(resolutions),
                "can_generate_proxy": random.choice([True, False])
            },
            "recent_activity": recent_activity
        })

    #  PROJECTS 
    creators = [u for u in users if u["role"] == "Creator"][:25]
    projects = []
    titles_used = {}
    for j in range(TOTAL):
        owner = creators[j % 25]
        used = titles_used.setdefault(owner["_id"]["$oid"], set())
        title = f"{random.choice(project_titles)} {random.randint(1, 20)}"
        while title in used:
            title = f"{random.choice(project_titles)} {random.randint(1, 20)}"
        used.add(title)

        created = datetime.now() - timedelta(days=random.randint(30, 400))
        projects.append({
            "_id": {"$oid": str(ObjectId())},
            "user_id": owner["_id"],
            "title": title,
            "target_region": random.choice(regions),
            "status": random.choice(statuses),
            "created_date": created.strftime("%Y-%m-%d")
        })

    # ASSETS 
    assets = []
    count_in_project = {}
    users_by_id = {u["_id"]["$oid"]: u for u in users}
    for i in range(TOTAL):
        project = projects[0] if i < 4 else random.choice(projects)
        project_oid = project["_id"]["$oid"]
        user = users_by_id[project["user_id"]["$oid"]]
        count_in_project[project_oid] = count_in_project.get(project_oid, 0) + 1

        file_format = random.choice(user["media_permissions"]["allowed_formats"])
        is_audio = file_format == '.wav'
        drive = random.choice(user["media_permissions"]["assigned_drives"])
        slug = project["title"].replace(' ', '_')
        created = datetime.strptime(project["created_date"], "%Y-%m-%d")

        # Tags embed the global tag's id and name
        assigned_tags = [{"tag_id": t["_id"], "tag_name": t["tag_name"]} for t in random.sample(tags, random.randint(1, 4))]

        # Audit logs
        audit_logs = []
        for _ in range(random.randint(2, 3)):
            log_time = created + timedelta(days=random.randint(1, 30))
            audit_logs.append({
                "_id": {"$oid": str(ObjectId())},
                "action": random.choice(actions),
                "timestamp": log_time.strftime("%Y-%m-%d %H:%M:%S"),
                "performed_by": user["email"],
                "tasks": [{
                    "_id": {"$oid": str(ObjectId())},
                    "task_name": random.choice(task_names),
                    "completed": random.choice([True, False])
                } for _ in range(random.randint(1, 3))]
            })

        asset_created = created + timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))
        assets.append({
            "_id": {"$oid": str(ObjectId())},
            "project_id": {"$oid": project_oid},
            "user_id": user["_id"],
            "filename": f"{slug}_{'AUD' if is_audio else 'A'}{count_in_project[project_oid]:03d}{file_format}",
            "file_format": file_format,
            "file_size_gb": round(random.uniform(0.1, 2.0) if is_audio else random.uniform(1.5, 180.0), 2),
            "resolution": "N/A" if is_audio else random.choice(resolutions),
            "drive_location": drive,
            "has_proxy": False if is_audio else random.random() < (0.7 if file_format in ('.mp4', '.mov') else 0.35),
            "created_timestamp": asset_created.strftime("%Y-%m-%d %H:%M:%S"),
            "tags": assigned_tags,
            "audit_logs": audit_logs
        })

    return users, projects, assets, tags

# Generate datasets
users_data, projects_data, assets_data, tags_data = generate_data()

# Export JSON files (import with mongoimport --jsonArray)
for filename, data in (('users.json', users_data), ('projects.json', projects_data), ('assets.json', assets_data), ('tags.json', tags_data)):
    with open(filename, 'w', encoding='utf-8') as fout:
        json.dump(data, fout, indent=4)
        print(f"Created {filename} ({len(data)} documents)")