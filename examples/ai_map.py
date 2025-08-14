from oxylabs_ai_studio.apps.ai_map import AiMap


ai_map = AiMap(api_key="<API_KEY>")

payload = {
    "url": "https://career.oxylabs.io",
    "user_prompt": "job ad pages",
    "return_sources_limit": 10,
    "geo_location": None,
    "render_javascript": False,
}
result = ai_map.map(**payload)
print(result.data)