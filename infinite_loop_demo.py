import time
from openai import OpenAI

# A simple script simulating a runaway agent loop
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy" 
)

print("Starting autonomous agent loop...")
print("Goal: Self-correcting code generation")
print("--------------------------------------------------")

iteration = 1
while True:
    print(f"[Iteration {iteration}] Sending prompt to LLM...")
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "user", "content": "The code failed with a SyntaxError. Please fix it."}
            ],
            max_tokens=50,
            stream=False
        )
        print(f"[Iteration {iteration}] Received response. Executing generated code...")
        time.sleep(1)
        print(f"[Iteration {iteration}] Code execution failed. Looping again...\n")
        iteration += 1
    except Exception as e:
        print("\n" + "="*50)
        print("[!] FATAL ERROR ENCOUNTERED [!]")
        print("="*50)
        print(f"Agent Loop Broken: {e}")
        print("="*50)
        break
