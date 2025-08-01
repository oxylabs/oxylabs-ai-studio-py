from oxylabs_ai_studio.apps.ai_map import AiMap


map = AiMap(api_key="<API_KEY>")

payload = {
    "url": "https://career.oxylabs.io",
    "user_prompt": "job ad pages",
    "return_sources_limit": 10,
    "max_depth": 1,
    "geo_location": None,
    "render_javascript": False,
}
result = map.map(**payload)
print(result.data)