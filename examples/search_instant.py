from oxylabs_ai_studio.apps.ai_search import AiSearch


search = AiSearch(api_key="<API_KEY>")

query = "lasagna recipes"
result = search.instant_search(
    query=query,
    limit=5,
    geo_location="United States",
)
print(result.data)
