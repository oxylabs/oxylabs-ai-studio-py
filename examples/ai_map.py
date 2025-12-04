from oxylabs_ai_studio.apps.ai_map import AiMap


ai_map = AiMap(api_key="<API_KEY>")
payload = {
    "url": "https://oxylabs.io",
    "search_keywords": ["blog"],
    "max_crawl_depth": 3,
    "limit": 50,
    "render_javascript": False,
    "include_sitemap": True,
    "max_credits": None,
    "allow_subdomains": False,
    "allow_external_domains": False,
}
result = ai_map.map(**payload)
print(result.data)