from oxylabs_ai_studio.apps.ai_map import AiMap

ai_map = AiMap(api_key="<API_KEY>")

payload = {
    "url": "https://oxylabs.io",
    "user_prompt": "find product pages",
    "return_sources_limit": 10,
    "include_sitemap": False,
    "include_paths": [".*/?products/.*"],
}
result = ai_map.map(**payload)
print(result.data)

