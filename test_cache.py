"""
Test script to verify semantic caching is working.
Run this after starting your FastAPI server.
"""
import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_cache():
    print("\n" + "="*60)
    print("SEMANTIC CACHE VERIFICATION TEST")
    print("="*60)
    
    # Test 1: First query (should MISS cache, call LLM)
    print("\n[TEST 1] First query - Should MISS cache and call LLM")
    print("-" * 60)
    query1 = "What is Firas's current role?"
    
    start = time.time()
    response1 = requests.post(
        f"{BASE_URL}/chat",
        json={"message": query1}
    )
    duration1 = time.time() - start
    
    print(f"Query: {query1}")
    print(f"Status: {response1.status_code}")
    print(f"Response time: {duration1:.2f}s")
    if response1.status_code == 200:
        answer1 = response1.json()["answer"]
        print(f"Answer preview: {answer1[:100]}...")
    
    # Test 2: Same query (should HIT cache)
    print("\n[TEST 2] Same query - Should HIT cache (fast response)")
    print("-" * 60)
    
    time.sleep(1)  # Small delay
    
    start = time.time()
    response2 = requests.post(
        f"{BASE_URL}/chat",
        json={"message": query1}  # Same query
    )
    duration2 = time.time() - start
    
    print(f"Query: {query1}")
    print(f"Status: {response2.status_code}")
    print(f"Response time: {duration2:.2f}s")
    if response2.status_code == 200:
        answer2 = response2.json()["answer"]
        print(f"Answer preview: {answer2[:100]}...")
    
    # Test 3: Similar query (should HIT cache if similarity > 0.95)
    print("\n[TEST 3] Similar query - May HIT cache depending on similarity")
    print("-" * 60)
    query3 = "What job does Firas have now?"
    
    time.sleep(1)
    
    start = time.time()
    response3 = requests.post(
        f"{BASE_URL}/chat",
        json={"message": query3}
    )
    duration3 = time.time() - start
    
    print(f"Query: {query3}")
    print(f"Status: {response3.status_code}")
    print(f"Response time: {duration3:.2f}s")
    if response3.status_code == 200:
        answer3 = response3.json()["answer"]
        print(f"Answer preview: {answer3[:100]}...")
    
    # Summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"Test 1 (Cache MISS): {duration1:.2f}s")
    print(f"Test 2 (Cache HIT):  {duration2:.2f}s")
    print(f"Test 3 (Similar):    {duration3:.2f}s")
    print()
    print("Expected behavior:")
    print("- Test 1: Slow (2-10s) - LLM call")
    print("- Test 2: Fast (<1s) - Cache hit")
    print("- Test 3: Fast if similarity > 0.95, else slow")
    print()
    print("Check server logs for [CACHE HIT] and [CACHE MISS] messages")
    print("="*60)

if __name__ == "__main__":
    try:
        test_cache()
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to server at http://127.0.0.1:8000")
        print("Make sure the FastAPI server is running:")
        print("  uvicorn app.main:app --reload --port 8000")
    except Exception as e:
        print(f"\nERROR: {e}")
