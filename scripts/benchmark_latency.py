import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("UPSTREAM_API_KEY")
BASE_URL = os.getenv("UPSTREAM_BASE_URL")

if not API_KEY or not BASE_URL:
    print("Error: UPSTREAM_API_KEY or UPSTREAM_BASE_URL missing in .env")
    exit(1)

PAYLOAD = {
    "model": "openai/gpt-oss-20b",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 10,
    "stream": False
}

def measure_direct():
    latencies = []
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    with httpx.Client() as client:
        # warm up
        client.post(f"{BASE_URL}/chat/completions", headers=headers, json=PAYLOAD)
        for i in range(5):
            start = time.perf_counter()
            resp = client.post(f"{BASE_URL}/chat/completions", headers=headers, json=PAYLOAD)
            resp.raise_for_status()
            latencies.append((time.perf_counter() - start) * 1000)
    return sum(latencies) / len(latencies)

def measure_proxy():
    latencies = []
    headers = {
        "Authorization": "Bearer dummy-key",
        "Content-Type": "application/json"
    }
    with httpx.Client() as client:
        # warm up
        client.post("http://localhost:8000/v1/budget/reset")
        client.post("http://localhost:8000/v1/chat/completions", headers=headers, json=PAYLOAD)
        for i in range(5):
            client.post("http://localhost:8000/v1/budget/reset")
            start = time.perf_counter()
            resp = client.post("http://localhost:8000/v1/chat/completions", headers=headers, json=PAYLOAD)
            if resp.status_code != 200:
                print("Proxy Error:", resp.text)
                continue
            latencies.append((time.perf_counter() - start) * 1000)
    return sum(latencies) / len(latencies)

print("Starting benchmark...")
print("Measuring DIRECT latency (5 requests)...")
direct_avg = measure_direct()
print(f"Average Direct Latency: {direct_avg:.2f} ms")

print("\nMeasuring PROXY latency (5 requests)...")
proxy_avg = measure_proxy()
print(f"Average Proxy Latency:  {proxy_avg:.2f} ms")

overhead = proxy_avg - direct_avg
print(f"\nTotal Proxy Overhead: {overhead:.2f} ms")
