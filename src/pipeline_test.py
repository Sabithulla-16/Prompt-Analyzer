from intent_extractor import extract_intent
from filter_tools import filter_tools

prompt = "Create a professional logo for my startup"

intent = extract_intent(prompt)
tools = filter_tools(intent)

print("Intent:", intent)
print("Matched tools:")
for tool in tools:
    print("-", tool["name"])