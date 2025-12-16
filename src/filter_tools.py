ACTION_ALIASES = {
    "convert": ["convert", "transcribe"],
    "generate": ["generate", "create"],
    "summarize": ["summarize"],
    "analyze": ["analyze"],
    "translate": ["translate"]
}

def filter_tools(intent, tools):
    filtered = []
    allowed_actions = ACTION_ALIASES.get(intent["action"], [intent["action"]])

    for tool in tools:
        if tool["domain"] != intent["domain"]:
            continue

        if not any(a in tool["actions"] for a in allowed_actions):
            continue

        pricing = intent["constraints"]["pricing"]
        if pricing != "any" and tool["pricing"] != pricing:
            continue

        filtered.append(tool)

    return filtered