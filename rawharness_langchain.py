# Way 3 of 4: LangChain — the loop disappears.
# Same base scenario as rawharness_text.py: real get_weather (Open-Meteo),
# prompt "What's the weather in XAA?". create_agent runs model->tool->model
# until done; there is no visible while-loop, stop_reason check, or tool dispatch.
#
# Targets LangChain 1.0 (`create_agent`). Install: pip install langchain langchain-anthropic
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_core.tools import tool

from tools.weather import get_weather as _get_weather   # shared core logic

load_dotenv()   # reads .env so ANTHROPIC_API_KEY is set

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return _get_weather(city)      # delegate to the shared implementation

agent = create_agent(
    model="anthropic:claude-opus-4-7",
    tools=[get_weather],
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in XAA?"}]}
)

# The framework owned the loop; we just read the resulting message history back out.
# Printing every message keeps the same "show your work" tracing as the raw version.
for i, message in enumerate(result["messages"]):
    print(f"--- message {i} ({message.type}) ---")
    message.pretty_print()

print("\nFINAL ANSWER:")
print(result["messages"][-1].content)
