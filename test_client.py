import time
from openai import OpenAI

# Initialize the OpenAI client to point to our local proxy
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy" # The proxy will use the real key
)

print("Sending request to local proxy...")
start_time = time.time()

try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b", # groq supported model
        messages=[
            {"role": "user", "content": "Say hello"}
        ],
        max_tokens=20,
        stream=False
    )
    end_time = time.time()
    latency = end_time - start_time
    
    print("\n--- Proxy Response ---")
    print(response.choices[0].message.content)
    print(f"\n--- Latency: {latency:.4f} seconds ---")
except Exception as e:
    print(f"Error: {e}")
