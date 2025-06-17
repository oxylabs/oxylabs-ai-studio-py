from oxylabs_ai_studio.apps.ai_scraper import AiScraper

scraper = AiScraper(api_key="<API_KEY>")

schema = scraper.generate_schema(prompt="want to parse developer, platform, type, price game title, genre (array) and description")
print(f"Generated schema: {schema}")

url = "https://sandbox.oxylabs.io/products/3"
result = scraper.scrape(
    url=url,
    output_format="json",
    schema=schema,
    render_javascript=False,
)
print(result)
