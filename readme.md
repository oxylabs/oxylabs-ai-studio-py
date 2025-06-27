# OxyLabs AI Studio Python SDK

A simple Python SDK for interacting with the Oxy Studio AI API.

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

---
See the [examples](https://github.com/oxylabs/oxylabs-ai-studio-py/tree/main/examples) folder for usage examples of each method. Each method has corresponding async version.
