from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Point LangChain to your local circuit breaker
llm = ChatOpenAI(
    model="gpt-4o-mini", 
    base_url="http://localhost:8000/v1", 
    api_key="dummy-key-not-needed",
    max_retries=0
)

print("Sending request through circuit breaker...")
try:
    response = llm.invoke([HumanMessage(content="Explain quantum computing in one sentence.")])
    print(response.content)
except Exception as e:
    print(f"Proxy intercepted: {e}")
