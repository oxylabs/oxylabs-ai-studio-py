# OxyLabs AI Studio Python SDK

[![AI-Studio Python (1)](https://github.com/oxylabs/oxylabs-ai-studio-py/blob/main/Ai-Studio2.png)](https://aistudio.oxylabs.io/?utm_source=877&utm_medium=affiliate&utm_campaign=ai_studio&groupid=877&utm_content=ai-studio-js-github&transaction_id=102f49063ab94276ae8f116d224b67) 

[![](https://dcbadge.limes.pink/api/server/Pds3gBmKMH?style=for-the-badge&theme=discord)](https://discord.gg/Pds3gBmKMH) [![YouTube](https://img.shields.io/badge/YouTube-Oxylabs-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@oxylabs)

A simple Python SDK for seamlessly interacting with [Oxylabs AI Studio API](https://aistudio.oxylabs.io/) services, including AI-Scraper, AI-Crawler, AI-Browser-Agent and other data extraction tools.

## Requirements
- python 3.10 and above
- API KEY

## Installation

```bash
pip install oxylabs-ai-studio
```

## Usage

### Crawl (`AiCrawler.crawl`)

```python

from oxylabs_ai_studio.apps.ai_crawler import AiCrawler

crawler = AiCrawler(api_key="<API_KEY>")

url = "https://oxylabs.io"
result = crawler.crawl(
    url=url,
    user_prompt="Find all pages with proxy products pricing",
    output_format="markdown",
    render_javascript=False,
    return_sources_limit=3,
    geo_location="United States",
)
print("Results:")
for item in result.data:
    print(item, "\n")

```

**Parameters:**
- `url` (str): Starting URL to crawl (**required**)
- `user_prompt` (str): Natural language prompt to guide extraction (**required**)
- `output_format` (Literal["json", "markdown", "csv", "toon"]): Output format (default: "markdown")
- `schema` (dict | None): Json schema for structured extraction (required if output_format is "json", "csv" or "toon")
- `render_javascript` (bool): Render JavaScript (default: False)
- `return_sources_limit` (int): Max number of sources to return (default: 25)
- `geo_location` (str): Proxy location in ISO2 format or country canonical name. See [docs](https://developers.oxylabs.io/scraping-solutions/web-scraper-api/features/localization/proxy-location#list-of-supported-geo_location-values)
- `max_credits` (int | None): Maximum of credits to use (optional)

### Scrape (`AiScraper.scrape`)

```python
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

```
**Parameters:**
- `url` (str): Target URL to scrape (**required**)
- `output_format` (Literal["json", "markdown", "csv", "screenshot", "toon"]): Output format (default: "markdown")
- `schema` (dict | None): JSON schema for structured extraction (required if output_format is "json", "csv" or "toon")
- `render_javascript` (bool | string): Render JavaScript. Can be set to "auto", meaning the service will detect if rendering is needed (default: False)
- `geo_location` (str): Proxy location in ISO2 format or country canonical name. See [docs](https://developers.oxylabs.io/scraping-solutions/web-scraper-api/features/localization/proxy-location#list-of-supported-geo_location-values)
- `user_agent` (str): User-Agent request header. See more at https://developers.oxylabs.io/scraping-solutions/web-scraper-api/features/http-context-and-job-management/user-agent-type.

### Browser Agent (`BrowserAgent.run`)

```python
from oxylabs_ai_studio.apps.browser_agent import BrowserAgent

browser_agent = BrowserAgent(api_key="<API_KEY>")

schema = browser_agent.generate_schema(
    prompt="game name, platform, review stars and price"
)
print("schema: ", schema)

prompt = "Find if there is game 'super mario odyssey' in the store. If there is, find the price. Use search bar to find the game."
url = "https://sandbox.oxylabs.io/"
result = browser_agent.run(
    url=url,
    user_prompt=prompt,
    output_format="json",
    schema=schema,
)
print(result.data)
```

**Parameters:**
- `url` (str): Starting URL to browse (**required**)
- `user_prompt` (str): Natural language prompt for extraction (**required**)
- `output_format` (Literal["json", "markdown", "html", "screenshot", "csv", "toon"]): Output format (default: "markdown")
- `schema` (dict | None): Json schema for structured extraction (required if output_format is "json", "csv" or "toon")
- `geo_location` (str): Proxy location in ISO2 format or country canonical name. For example 'Germany' (capitalized).

### Search (`AiSearch.search`)

```python
from oxylabs_ai_studio.apps.ai_search import AiSearch


search = AiSearch(api_key="<API_KEY>")

query = "lasagna recipe"
result = search.search(
    query=query,
    limit=5,
    render_javascript=False,
    return_content=True,
)
print(result.data)

# Or for fast search
result = search.instant_search(
    query=query,
    limit=10,
)
print(result.data)
```

**Parameters:**
- `query` (str): What to search for (**required**)
- `limit` (int): Maximum number of results to return (default: 10, maximum: 50)
- `render_javascript` (bool): Render JavaScript (default: False)
- `return_content` (bool): Whether to return markdown contents in results (default: True)
- `geo_location` (*string*): ISO 2-letter format, country name, coordinate formats are supported. See more at [SERP Localization](https://developers.oxylabs.io/scraping-solutions/web-scraper-api/features/localization/serp-localization).

> **Note:** When `limit <= 10` and `return_content=False`, the search automatically uses the instant endpoint (`/search/instant`) which returns results immediately without polling, providing faster response times.

Instant search supported parameters:
- `query` (*string*): The search query.
- `limit` (*integer*): The maximum number of search results to return. Maximum: 10.
- `geo_location` (*string*): Google's canonical name of the location. See more at [Google Ads GeoTargets](https://developers.google.com/google-ads/api/data/geotargets).


### Map (`AiMap.map`)
```python
from oxylabs_ai_studio.apps.ai_map import AiMap


ai_map = AiMap(api_key="<API_KEY>")
payload = {
    "url": "https://career.oxylabs.io",
    "search_keywords": ["career", "jobs", "vacancy"],
    "user_prompt": "job ad pages",
    "max_crawl_depth": 2,
    "limit": 10,
    "geo_location": "Germany",
    "render_javascript": False,
    "include_sitemap": True,
    "max_credits": None,
    "allow_subdomains": False,
    "allow_external_domains": False,
}
result = ai_map.map(**payload)
print(result.data)
```
**Parameters:**
- `url` (str): Starting URL or domain to map (**required**)
- `search_keywords` (list[str]): Keywords for URLs paths filtering (default: None)
- `user_prompt` (str | None): Natural language prompt for keyword search. Can be used together with 'search_keywords' or standalone (optional)
- `max_crawl_depth` (int): Max crawl depth (1..5, default: 1)
- `limit` (int): Max number of URLs to return (default: 25)
- `geo_location` (str): Proxy location in ISO2 format or country canonical name. See [docs](https://developers.oxylabs.io/scraping-solutions/web-scraper-api/features/localization/proxy-location#list-of-supported-geo_location-values)
- `render_javascript` (bool): JavaScript rendering (default: False)
- `include_sitemap` (bool): Whether to include sitemap as seed (default: True)
- `max_credits` (int | None): Maximum of credits to use (optional)
- `allow_subdomains` (bool): Include subdomains (default: False)
- `allow_external_domains` (bool): Include external domains (default: False)

---
See the [examples](https://github.com/oxylabs/oxylabs-ai-studio-py/tree/main/examples) folder for usage examples of each method. Each method has corresponding async version.
