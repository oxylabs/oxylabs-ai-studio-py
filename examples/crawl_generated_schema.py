from oxylabs_ai_studio.apps.ai_crawl import AiCrawl

crawler = AiCrawl(api_key="<API_KEY>")

schema = crawler.generate_schema(
    prompt="proxy plans which have name, price, and features",
)
print("schema: ", schema)

url = "https://oxylabs.io"
result = crawler.crawl(
    url=url,
    user_prompt="Find all pages with proxy products pricing",
    output_format="json",
    schema=schema,
    render_javascript=False,
)
print("Results:")
for item in result.data:
    print(item, "\n")
