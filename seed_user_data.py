#!/usr/bin/env python3
"""Seed Supabase with sample user data and activity logs for testing"""
import json
from datetime import datetime, timedelta
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Supabase credentials not configured in .env")
    exit(1)

try:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"✓ Connected to Supabase: {SUPABASE_URL}")
except Exception as e:
    print(f"❌ Failed to connect to Supabase: {e}")
    exit(1)

# Sample activity data (matches actual schema: id, event_type, entity_id, user_id, created_at)
now = datetime.utcnow()
activities = [
    {
        "event_type": "document_approved",
        "entity_id": "doc_001",
        "user_id": "user@company.com",
        "created_at": (now - timedelta(hours=2)).isoformat() + "Z"
    },
    {
        "event_type": "answer_generated",
        "entity_id": "ans_001",
        "user_id": "user@company.com",
        "created_at": (now - timedelta(hours=1)).isoformat() + "Z"
    },
    {
        "event_type": "document_ingested",
        "entity_id": "doc_002",
        "user_id": "admin@company.com",
        "created_at": now.isoformat() + "Z"
    },
    {
        "event_type": "export_created",
        "entity_id": "exp_001",
        "user_id": "user@company.com",
        "created_at": (now - timedelta(hours=3)).isoformat() + "Z"
    },
    {
        "event_type": "validation_completed",
        "entity_id": "val_001",
        "user_id": "reviewer@company.com",
        "created_at": (now - timedelta(hours=4)).isoformat() + "Z"
    },
]

print("\n📝 Seeding activity data...")
for activity in activities:
    try:
        result = client.table("activity").insert(activity).execute()
        print(f"  ✓ Added: {activity['event_type']}")
    except Exception as e:
        print(f"  ⚠ Error adding {activity['event_type']}: {str(e)[:100]}")

# Sample activity logs (matches schema: id, user_id, action_type, metadata, created_at)
activity_logs = [
    {
        "user_id": "user@company.com",
        "action_type": "document_review",
        "metadata": json.dumps({"document": "Workplace Conduct", "status": "approved"}),
        "created_at": (now - timedelta(hours=2)).isoformat() + "Z"
    },
    {
        "user_id": "admin@company.com",
        "action_type": "system_ingestion",
        "metadata": json.dumps({"file": "sample_workplace_conduct.txt", "chunks": 6}),
        "created_at": now.isoformat() + "Z"
    },
]

print("\n📊 Seeding activity logs...")
for log in activity_logs:
    try:
        result = client.table("activity_logs").insert(log).execute()
        print(f"  ✓ Added log: {log['action_type']}")
    except Exception as e:
        print(f"  ⚠ Error adding log {log['action_type']}: {str(e)[:100]}")

# Sample user stats (matches schema: id, user_id, total_actions, total_logins, last_active, created_at, updated_at)
user_stats = [
    {
        "user_id": "user@company.com",
        "total_actions": 45,
        "total_logins": 12,
        "last_active": now.isoformat() + "Z",
        "created_at": (now - timedelta(days=30)).isoformat() + "Z",
        "updated_at": now.isoformat() + "Z"
    },
    {
        "user_id": "admin@company.com",
        "total_actions": 156,
        "total_logins": 8,
        "last_active": now.isoformat() + "Z",
        "created_at": (now - timedelta(days=60)).isoformat() + "Z",
        "updated_at": now.isoformat() + "Z"
    },
    {
        "user_id": "reviewer@company.com",
        "total_actions": 28,
        "total_logins": 15,
        "last_active": (now - timedelta(hours=4)).isoformat() + "Z",
        "created_at": (now - timedelta(days=45)).isoformat() + "Z",
        "updated_at": (now - timedelta(hours=4)).isoformat() + "Z"
    }
]

print("\n👤 Seeding user stats...")
for user_stat in user_stats:
    try:
        result = client.table("user_stats").insert(user_stat).execute()
        print(f"  ✓ Added stats for: {user_stat['user_id']}")
    except Exception as e:
        print(f"  ⚠ Error adding user stats for {user_stat['user_id']}: {str(e)[:100]}")

print("\n✓ Seeding complete!")
print("\nSample data added:")
print(f"  - {len(activities)} activity records")
print(f"  - {len(activity_logs)} activity logs")
print(f"  - {len(user_stats)} user stat records")
print("\nFrontend should now show real user data from Supabase!")
