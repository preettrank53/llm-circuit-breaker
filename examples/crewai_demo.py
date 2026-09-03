from crewai import Agent, Task, Crew, LLM

# Configure CrewAI to use the local circuit breaker natively
proxy_llm = LLM(
    model="gpt-4o-mini",
    custom_openai=True, 
    base_url="http://localhost:8000/v1",
    api_key="dummy-key"
)

researcher = Agent(
    role="Researcher",
    goal="Discover facts",
    backstory="You are a researcher.",
    llm=proxy_llm
)

task = Task(description="Tell me a joke.", expected_output="A joke.", agent=researcher)

crew = Crew(
    agents=[researcher], 
    tasks=[task],
    planning=True,
    planning_llm=proxy_llm # Prevent CrewAI from bypassing the proxy for planning 
)

try:
    print(crew.kickoff())
except Exception as e:
    print(f"Proxy intercepted the agent: {e}")
