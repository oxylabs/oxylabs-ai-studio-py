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
    geo_location="US",
)
print("Results:")
for item in result.data:
    print(item, "\n")

```

**Parameters:**
- `url` (str): Starting URL to crawl (**required**)
- `user_prompt` (str): Natural language prompt to guide extraction (**required**)
- `output_format` (Literal["json", "markdown"]): Output format (default: "markdown")
- `schema` (dict | None): OpenAPI schema for structured extraction (required if output_format is "json")
- `render_javascript` (bool): Render JavaScript (default: False)
- `return_sources_limit` (int): Max number of sources to return (default: 25)
- `geo_location` (str): proxy location in ISO2 format.

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
- `output_format` (Literal["json", "markdown"]): Output format (default: "markdown")
- `schema` (dict | None): OpenAPI schema for structured extraction (required if output_format is "json")
- `render_javascript` (bool): Render JavaScript (default: False)
- `geo_location` (str): proxy location in ISO2 format.

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
- `output_format` (Literal["json", "markdown", "html", "screenshot"]): Output format (default: "markdown")
- `schema` (dict | None): OpenAPI schema for structured extraction (required if output_format is "json")
- `geo_location` (str): proxy location in ISO2 format.

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
```

**Parameters:**
- `query` (str): What to search for (**required**)
- `limit` (int): Maximum number of results to return (default: 10, maximum: 50)
- `render_javascript` (bool): Render JavaScript (default: False)
- `return_content` (bool): Whether to return markdown contents in results (default: True)
- `geo_location` (str): search proxy location in ISO2 format.

### Map (`AiMap.map`)
```python
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
```
**Parameters:**
- `url` (str): Starting URL to crawl (**required**)
- `user_prompt` (str): Natural language prompt to guide extraction (**required**)
- `render_javascript` (bool): Render JavaScript (default: False)
- `return_sources_limit` (int): Max number of sources to return (default: 25)
- `geo_location` (str): proxy location in ISO2 format.

---
See the [examples](https://github.com/oxylabs/oxylabs-ai-studio-py/tree/main/examples) folder for usage examples of each method. Each method has corresponding async version.
