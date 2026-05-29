import os, requests
from dotenv import load_dotenv
import json

from tools.weather import get_weather, GET_WEATHER_TOOL   # shared tool: logic + schema


load_dotenv()   # reads .env so ANTHROPIC_API_KEY is set without exporting it first

API_URL = "https://api.anthropic.com/v1/messages"

HEADERS = {
    "x-api-key": os.environ["ANTHROPIC_API_KEY"],
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

TOOLS = [GET_WEATHER_TOOL]

def run_tool(name, args):
    if name == "get_weather":
        return get_weather(args["city"])
    return f"Unknown tool: {name}"

messages = [{"role": "user", "content": "What's the weather in XAA?"}]
times = 0                                            # <-- initialize ONCE, before the loop
while True:                                          # <-- the harness loop
    print(f"Here is the message history up to this point (turn {times}):{json.dumps(messages, indent=2)}")

    resp = requests.post(API_URL, headers=HEADERS, json={
        "model": "claude-opus-4-7",
        "max_tokens": 1024,
        "tools": TOOLS,
        "messages": messages,
    }).json()

    messages.append({"role": "assistant", "content": resp["content"]})
    print(f"MODEL RESPONSE: {times}")
    print(json.dumps(resp, indent=2))

    if resp["stop_reason"] != "tool_use":            # model is done
        print("".join(b["text"] for b in resp["content"] if b["type"] == "text"))
        break
    # If the model is not done... 
    tool_results = []                                # run every requested tool
    for block in resp["content"]:
        if block["type"] == "tool_use":
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block["id"],
                "content": run_tool(block["name"], block["input"]),
            })
    messages.append({"role": "user", "content": tool_results})
    print(f"TOOL RESULTS ' ' {times}: {tool_results}")

    times += 1
