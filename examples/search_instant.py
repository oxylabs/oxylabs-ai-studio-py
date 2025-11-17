"""Example of using the instant search feature."""

from oxylabs_ai_studio.apps.ai_search import AiSearch

# Initialize the search client
search = AiSearch()

# Perform an instant search
result = search.search_instant(
    query="weather today",
    geo_location="United States"
)

# Print the results
print(f"Run ID: {result.run_id}")
print(f"Status: completed")
print(f"\nSearch Results:")
if result.data:
    for idx, item in enumerate(result.data, 1):
        print(f"\n{idx}. {item.title}")
        print(f"   URL: {item.url}")
        print(f"   Description: {item.description}")
        if item.content:
            print(f"   Content preview: {item.content[:100]}...")
else:
    print("No results found")

