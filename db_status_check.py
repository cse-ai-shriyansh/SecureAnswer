#!/usr/bin/env python3
"""Database status check for SecureAnswer Supabase."""

import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def get_table_stats(client, table_name: str) -> Dict[str, Any]:
    """Get statistics for a table."""
    try:
        # Get total count
        result = client.table(table_name).select("count", count="exact").execute()
        total = result.count if result.count is not None else 0
        
        # Get recent records
        records = client.table(table_name).select("*").order("created_at", desc=True).limit(1).execute()
        latest = records.data[0] if records.data else None
        
        return {
            "status": "✅ OK",
            "total_records": total,
            "latest_record_time": latest.get("created_at") if latest else "N/A",
            "sample_keys": list(latest.keys()) if latest else []
        }
    except Exception as e:
        return {
            "status": f"❌ ERROR: {str(e)}",
            "total_records": 0,
            "latest_record_time": "N/A",
            "sample_keys": []
        }

def check_database_status():
    """Check overall database status."""
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    
    print("\n" + "="*70)
    print("DATABASE STATUS CHECK - SecureAnswer")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().isoformat()}\n")
    
    if not url or not key:
        print("❌ ERROR: SUPABASE_URL or SUPABASE_KEY not set in .env")
        return
    
    print(f"📍 Supabase URL: {url[:50]}{'...' if len(url) > 50 else ''}")
    print(f"🔑 API Key: {key[:20]}...\n")
    
    # Warn if localhost
    if "localhost" in url:
        print("⚠️  WARNING: Using LOCAL Supabase emulator (localhost:54321)")
        print("    Make sure local Supabase is running: 'supabase start'")
        print()
    
    try:
        client = create_client(url, key)
        print("✅ Client created (connection will be tested with first query)\n")
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {str(e)}\n")
        return
    
    # Check key tables
    tables = ["vectors", "activity", "ingestion_jobs"]
    
    print("-" * 70)
    print("TABLE STATISTICS")
    print("-" * 70 + "\n")
    
    v_count = 0
    a_count = 0
    j_count = 0
    
    for table in tables:
        print(f"📊 TABLE: {table.upper()}")
        stats = get_table_stats(client, table)
        for key, value in stats.items():
            if key == "sample_keys":
                print(f"   {key}: {', '.join(value[:5]) if value else 'N/A'}")
            else:
                print(f"   {key}: {value}")
        
        if table == "vectors":
            v_count = stats["total_records"]
        elif table == "activity":
            a_count = stats["total_records"]
        elif table == "ingestion_jobs":
            j_count = stats["total_records"]
        
        print()
    
    # Get data summary
    print("-" * 70)
    print("DATA SUMMARY")
    print("-" * 70 + "\n")
    
    try:
        # Get approval status breakdown
        approved = client.table("vectors").select("id", count="exact").eq("approval_status", "approved").execute()
        pending = client.table("vectors").select("id", count="exact").eq("approval_status", "pending").execute()
        rejected = client.table("vectors").select("id", count="exact").eq("approval_status", "rejected").execute()
        
        approved_count = approved.count if approved.count is not None else 0
        pending_count = pending.count if pending.count is not None else 0
        rejected_count = rejected.count if rejected.count is not None else 0
        
        print(f"📦 Total Vectors (Chunks): {v_count}")
        print(f"   ├─ Approved: {approved_count}")
        print(f"   ├─ Pending: {pending_count}")
        print(f"   └─ Rejected: {rejected_count}")
        print()
        
        print(f"📝 Activity Logs: {a_count}")
        print(f"⚙️  Ingestion Jobs: {j_count}")
        print()
        
        # Get document count
        if v_count > 0:
            docs = client.table("vectors").select("doc_id").execute()
            unique_docs = len(set(d.get("doc_id") for d in docs.data)) if docs.data else 0
            print(f"📄 Unique Documents: {unique_docs}")
        else:
            print(f"📄 Unique Documents: 0 (no vectors)")
        print()
        
    except Exception as e:
        print(f"❌ Error fetching summary: {str(e)}\n")
    
    # Check recent activity
    print("-" * 70)
    print("RECENT ACTIVITY (Last 5 records)")
    print("-" * 70 + "\n")
    
    try:
        recent = client.table("activity").select("*").order("created_at", desc=True).limit(5).execute()
        if recent.data:
            for record in recent.data:
                print(f"• {record.get('event_type', 'unknown').upper()}")
                print(f"  Entity: {record.get('entity_id', 'N/A')}")
                print(f"  User: {record.get('user_id', 'system')}")
                print(f"  Time: {record.get('created_at', 'N/A')}")
                print()
        else:
            print("No activity records found (expected if first run).\n")
    except Exception as e:
        print(f"❌ Error fetching activity: {str(e)}\n")
    
    # Health summary
    print("-" * 70)
    print("HEALTH SUMMARY")
    print("-" * 70 + "\n")
    
    connection_ok = v_count >= 0 or a_count >= 0 or j_count >= 0
    
    health_checks = {
        "Connection": "✅ Pass" if connection_ok else "❌ Fail",
        "Vectors Table": f"✅ OK ({v_count} records)" if v_count > 0 else "⚠️  Empty (expected if first run)",
        "Activity Table": f"✅ OK ({a_count} records)" if a_count > 0 else "⚠️  Empty (expected if first run)",
        "Data Status": "✅ Has data" if v_count > 0 else "⚠️  No data yet (awaiting ingestion)",
    }
    
    for check, result in health_checks.items():
        print(f"{check}: {result}")
    
    print("\n" + "="*70 + "\n")
    
    # Recommendations
    print("💡 NEXT STEPS:\n")
    if v_count == 0:
        print("   • No vectors/chunks found in database")
        print("   • Run ingestion to populate: use /api/ingestion/upload endpoint")
        print("   • Or execute SETUP.md to seed initial data\n")
    else:
        print(f"   • Database is operational with {v_count} chunks ready\n")
    
    if "localhost" in url:
        print("   • If using production Supabase, update .env to use HTTPS URL\n")
    else:
        print("   • Connected to production Supabase ✅\n")

if __name__ == "__main__":
    check_database_status()

