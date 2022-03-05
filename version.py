def get_version() -> str:
    import json
    with open("manifest.json") as f:
        data = json.load(f)
    return data["version"] or "unknown"
__version__ = get_version()
