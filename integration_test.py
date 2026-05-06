#!/usr/bin/env python3
"""
Integration Test - Frontend to Backend RAG Pipeline
Tests the complete flow: frontend API client -> backend routes -> RAG services
"""

import sys
import os
import time
import requests
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configuration
BACKEND_URL = 'http://localhost:8000'
TEST_QUERY = 'What is SecureAnswer?'

def check_backend_running():
    """Check if backend is running"""
    try:
        response = requests.get(f'{BACKEND_URL}/', timeout=2)
        print(f"✅ Backend is running at {BACKEND_URL}")
        return True
    except requests.ConnectionError:
        print(f"❌ Backend is not running at {BACKEND_URL}")
        print(f"   Start it with: cd backend && uvicorn app:app --reload")
        return False

def test_health_endpoint():
    """Test health check endpoint"""
    try:
        response = requests.get(f'{BACKEND_URL}/api/health', timeout=5)
        print(f"✅ /api/health: {response.status_code}")
        print(f"   {json.dumps(response.json(), indent=2)[:200]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ /api/health failed: {e}")
        return False

def test_retrieval_endpoint():
    """Test retrieval endpoint"""
    try:
        response = requests.post(
            f'{BACKEND_URL}/api/retrieval',
            params={
                'query': TEST_QUERY,
                'top_k': 5,
                'use_llm': False
            },
            timeout=10
        )
        print(f"✅ /api/retrieval: {response.status_code}")
        data = response.json()
        print(f"   Retrieved {len(data.get('retrieval_chunks', []))} chunks")
        print(f"   Search time: {data.get('search_time_ms')} ms")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ /api/retrieval failed: {e}")
        return False

def test_generation_endpoint():
    """Test generation endpoint"""
    try:
        response = requests.post(
            f'{BACKEND_URL}/api/generate',
            params={
                'question': TEST_QUERY,
                'use_llm': False,
                'top_k': 5
            },
            timeout=10
        )
        print(f"✅ /api/generate: {response.status_code}")
        data = response.json()
        print(f"   Answer: {data.get('answer', 'N/A')[:100]}...")
        print(f"   Confidence: {data.get('confidence', 0):.2f}")
        print(f"   Generation time: {data.get('generation_time_ms')} ms")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ /api/generate failed: {e}")
        return False

def test_dashboard_endpoint():
    """Test dashboard endpoint"""
    try:
        response = requests.get(f'{BACKEND_URL}/api/dashboard', timeout=5)
        print(f"✅ /api/dashboard: {response.status_code}")
        data = response.json()
        print(f"   Total chunks: {data.get('total_chunks', 0)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ /api/dashboard failed: {e}")
        return False

def test_ingestion_endpoint():
    """Test ingestion status endpoint"""
    try:
        response = requests.get(f'{BACKEND_URL}/api/ingestion', timeout=5)
        print(f"✅ /api/ingestion: {response.status_code}")
        print(f"   Status: {response.json().get('status', 'unknown')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ /api/ingestion failed: {e}")
        return False

def main():
    print("=" * 70)
    print("🧪 FRONTEND-BACKEND INTEGRATION TEST")
    print("=" * 70)
    print()

    # Step 1: Check if backend is running
    print("1️⃣  Checking backend connection...")
    if not check_backend_running():
        print("\n⚠️  Cannot proceed without backend running!")
        return False
    print()

    # Step 2: Test endpoints
    print("2️⃣  Testing integration endpoints...")
    tests = [
        ("Health Check", test_health_endpoint),
        ("Retrieval", test_retrieval_endpoint),
        ("Generation", test_generation_endpoint),
        ("Dashboard", test_dashboard_endpoint),
        ("Ingestion", test_ingestion_endpoint),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n   Testing: {test_name}")
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()
    print(f"Result: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All integration tests passed!")
        print("\n📝 Next Steps:")
        print("  1. Start frontend: npm run dev")
        print("  2. Open http://localhost:5173")
        print("  3. Navigate to Answer Generation page")
        print("  4. Test query input and answer generation")
        print("  5. Check frontend browser console for any errors")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
