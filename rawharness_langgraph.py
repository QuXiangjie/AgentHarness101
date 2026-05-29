# Way 4 of 4: LangGraph — the loop, drawn as a graph.
# Same base scenario as rawharness_text.py: real get_weather (Open-Meteo),
# prompt "What's the weather in XAA?". The while-loop becomes a state graph:
# two nodes (model, tools) and an edge that loops tools -> model. A conditional
# edge (tools_condition) ends the run when the model stops calling tools --
# that's the `if stop_reason != "tool_use"` check from the raw version.
#
# Install: pip install langgraph langchain-anthropic
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

from tools.weather import get_weather as _get_weather   # shared core logic

load_dotenv()   # reads .env so ANTHROPIC_API_KEY is set

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return _get_weather(city)      # delegate to the shared implementation

tools = [get_weather]
llm = ChatAnthropic(model="claude-opus-4-7").bind_tools(tools)

def call_model(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

graph = StateGraph(MessagesState)
graph.add_node("model", call_model)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "model")
graph.add_conditional_edges("model", tools_condition)   # -> "tools" or END
graph.add_edge("tools", "model")                         # <-- loop back
app = graph.compile()

result = app.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in XAA?"}]}
)

# Same "show your work" tracing: print every message the graph accumulated.
for i, message in enumerate(result["messages"]):
    print(f"--- message {i} ({message.type}) ---")
    message.pretty_print()

print("\nFINAL ANSWER:")
print(result["messages"][-1].content)
