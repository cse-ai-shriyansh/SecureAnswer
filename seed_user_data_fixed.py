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

now = datetime.utcnow()

# First, seed users table
print("\n👤 Seeding users...")
users = [
    {
        "email": "user@company.com",
        "name": "John User",
        "role": "analyst"
    },
    {
        "email": "admin@company.com",
        "name": "Admin Account",
        "role": "admin"
    },
    {
        "email": "reviewer@company.com",
        "name": "Jane Reviewer",
        "role": "reviewer"
    }
]

for user in users:
    try:
        result = client.table("users").upsert(user, on_conflict="email").execute()
        print(f"  ✓ Seeded user: {user['email']}")
    except Exception as e:
        print(f"  ⚠ Error seeding user {user['email']}: {str(e)[:100]}")

# Seed activity table (using correct schema: id, event_type, entity_id, user_id, created_at)
print("\n📝 Seeding activity data...")
activities = [
    {
        "event_type": "document_approved",
        "entity_id": "doc_001",
        "user_id": "user@company.com",
        "created_at": (now - timedelta(hours=2)).isoformat()
    },
    {
        "event_type": "answer_generated",
        "entity_id": "answer_001",
        "user_id": "user@company.com",
        "created_at": (now - timedelta(hours=1)).isoformat()
    },
    {
        "event_type": "document_ingested",
        "entity_id": "doc_002",
        "user_id": "admin@company.com",
        "created_at": now.isoformat()
    },
    {
        "event_type": "validation_completed",
        "entity_id": "doc_001",
        "user_id": "reviewer@company.com",
        "created_at": (now - timedelta(hours=4)).isoformat()
    },
]

for activity in activities:
    try:
        result = client.table("activity").insert(activity).execute()
        print(f"  ✓ Added: {activity['event_type']}")
    except Exception as e:
        print(f"  ⚠ Error adding {activity['event_type']}: {str(e)[:100]}")

# Seed activity_logs table (using correct schema: id, user_id, action_type, metadata, created_at)
print("\n📋 Seeding activity logs...")
activity_logs = [
    {
        "user_id": "user@company.com",
        "action_type": "review_document",
        "metadata": json.dumps({"document": "Workplace Conduct Policy", "status": "approved"}),
        "created_at": (now - timedelta(hours=2)).isoformat()
    },
    {
        "user_id": "user@company.com",
        "action_type": "generate_answer",
        "metadata": json.dumps({"question": "What are workplace conduct guidelines?", "confidence": 0.92}),
        "created_at": (now - timedelta(hours=1)).isoformat()
    },
    {
        "user_id": "admin@company.com",
        "action_type": "ingest_document",
        "metadata": json.dumps({"file_name": "sample_workplace_conduct.txt", "chunks": 6}),
        "created_at": now.isoformat()
    },
]

for log in activity_logs:
    try:
        result = client.table("activity_logs").insert(log).execute()
        print(f"  ✓ Added: {log['action_type']}")
    except Exception as e:
        print(f"  ⚠ Error adding {log['action_type']}: {str(e)[:100]}")

# Seed user_stats table (using correct schema: id, user_id, total_actions, total_logins, last_active, created_at, updated_at)
print("\n📊 Seeding user stats...")
user_stats = [
    {
        "user_id": "user@company.com",
        "total_actions": 45,
        "total_logins": 12,
        "last_active": now.isoformat()
    },
    {
        "user_id": "admin@company.com",
        "total_actions": 156,
        "total_logins": 8,
        "last_active": now.isoformat()
    },
    {
        "user_id": "reviewer@company.com",
        "total_actions": 28,
        "total_logins": 5,
        "last_active": (now - timedelta(hours=1)).isoformat()
    }
]

for stat in user_stats:
    try:
        result = client.table("user_stats").upsert(stat, on_conflict="user_id").execute()
        print(f"  ✓ Added stats for: {stat['user_id']}")
    except Exception as e:
        print(f"  ⚠ Error adding stats for {stat['user_id']}: {str(e)[:100]}")

print("\n✓ Seeding complete!")
print("\nSample data added:")
print(f"  - {len(users)} users")
print(f"  - {len(activities)} activity records")
print(f"  - {len(activity_logs)} activity logs")
print(f"  - {len(user_stats)} user stats")
print("\n⚠️  If you still see 401 errors, run the RLS policies SQL in Supabase:")
print("   1. Go to SQL Editor in Supabase dashboard")
print("   2. Copy and paste content from: setup_rls_policies.sql")
print("   3. Execute the SQL")
print("\nFrontend should now show real user data from Supabase!")
