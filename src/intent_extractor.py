def extract_intent(prompt: str):
    p = prompt.lower()

    # ---------- DOMAIN ----------
    if any(w in p for w in [
        "logo", "image", "photo", "design", "art", "poster",
        "banner", "thumbnail", "illustration", "graphic", "branding"
    ]):
        domain = "Image"
        input_type = "text"
        output_type = "image"

    elif any(w in p for w in [
        "video", "reel", "clip", "movie", "animation",
        "short", "youtube", "instagram"
    ]):
        domain = "Video"
        input_type = "text"
        output_type = "video"

    elif any(w in p for w in [
        "audio", "voice", "speech", "song", "music",
        "podcast", "narration"
    ]):
        domain = "Audio"
        input_type = "text"
        output_type = "audio"

    elif any(w in p for w in [
        "code", "coding", "program", "python", "java",
        "javascript", "website", "app", "software", "api"
    ]):
        domain = "Code"
        input_type = "text"
        output_type = "code"

    else:
        domain = "Text"
        input_type = "text"
        output_type = "text"

    # ---------- ACTION ----------
    if any(w in p for w in ["summarize", "summary", "shorten"]):
        action = "summarize"
    elif any(w in p for w in ["analyze", "analysis", "explain", "review"]):
        action = "analyze"
    elif any(w in p for w in ["translate"]):
        action = "translate"
    elif any(w in p for w in [
        "convert", "transcribe", "speech to text", "audio to text"
    ]):
        action = "convert"
    else:
        action = "generate"

    # ---------- PRICING ----------
    if "free" in p:
        pricing = "free"
    elif "paid" in p or "premium" in p:
        pricing = "paid"
    else:
        pricing = "any"

    return {
        "domain": domain,
        "action": action,
        "input_type": input_type,
        "output_type": output_type,
        "use_case": prompt,
        "constraints": {"pricing": pricing}
    }