# Way 2 of 4: Claude SDK — same loop as the raw-HTTP version, but typed objects.
# Same base scenario as rawharness_text.py: real get_weather (Open-Meteo),
# prompt "What's the weather in XAA?", verbose turn-by-turn tracing.
from dotenv import load_dotenv
import json

import anthropic

from tools.weather import get_weather, GET_WEATHER_TOOL   # shared tool: logic + schema

load_dotenv()                       # reads .env so ANTHROPIC_API_KEY is set
client = anthropic.Anthropic()      # picks up ANTHROPIC_API_KEY from env

TOOLS = [GET_WEATHER_TOOL]

def run_tool(name, args):
    if name == "get_weather":
        return get_weather(args["city"])
    return f"Unknown tool: {name}"

messages = [{"role": "user", "content": "What's the weather in XAA?"}]
times = 0                                            # <-- initialize ONCE, before the loop
while True:                                          # <-- still YOUR loop (the SDK is just transport)
    print(f"Here is the message history up to this point (turn {times}):{json.dumps(messages, indent=2, default=str)}")

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        tools=TOOLS,
        messages=messages,
    )

    messages.append({"role": "assistant", "content": response.content})
    print(f"MODEL RESPONSE: {times}")
    print(response.model_dump_json(indent=2))

    if response.stop_reason != "tool_use":           # model is done
        print("".join(b.text for b in response.content if b.type == "text"))
        break
    # If the model is not done...
    tool_results = []                                # run every requested tool
    for block in response.content:
        if block.type == "tool_use":
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": run_tool(block.name, block.input),
            })
    messages.append({"role": "user", "content": tool_results})
    print(f"TOOL RESULTS ' ' {times}: {tool_results}")

    times += 1
