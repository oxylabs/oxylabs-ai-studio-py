
from oxylabs_ai_studio.apps.ai_crawler import AiCrawler

crawler = AiCrawler(api_key="<API_KEY>")

url = "https://oxylabs.io"
result = crawler.crawl(
    url=url,
    user_prompt="Find all pages with proxy products pricing",
    output_format="markdown",
    render_javascript=False,
    return_sources_limit=3,
)
print("Results:")
for item in result.data:
    print(item, "\n")

