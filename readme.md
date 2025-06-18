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

### Crawl (`AiCrawl.crawl`)
**Parameters:**
- `url` (str): Starting URL to crawl (**required**)
- `user_prompt` (str): Natural language prompt to guide extraction (**required**)
- `output_format` (Literal["json", "markdown"]): Output format (default: "markdown")
- `schema` (dict | None): OpenAPI schema for structured extraction (required if output_format is "json")
- `render_javascript` (bool): Render JavaScript (default: False)
- `return_sources_limit` (int): Max number of sources to return (default: 25)

### Scrape (`AiScraper.scrape`)
**Parameters:**
- `url` (str): Target URL to scrape (**required**)
- `output_format` (Literal["json", "markdown"]): Output format (default: "markdown")
- `schema` (dict | None): OpenAPI schema for structured extraction (required if output_format is "json")
- `render_javascript` (bool): Render JavaScript (default: False)

### Browser Agent (`BrowserAgent.run`)
**Parameters:**
- `url` (str): Starting URL to browse (**required**)
- `user_prompt` (str): Natural language prompt for extraction (**required**)
- `output_format` (Literal["json", "markdown", "html", "screenshot"]): Output format (default: "markdown")
- `schema` (dict | None): OpenAPI schema for structured extraction (required if output_format is "json")

### Search (`AiSearch.search`)
**Parameters:**
- `query` (str): What to search for (**required**)
- `limit` (int): Maximum number of results to return (default: 10, maximum: 50)
- `render_javascript` (bool): Render JavaScript (default: False)
- `return_content` (bool): Whether to return markdown contents in results (default: True)

---
See the [examples](https://github.com/oxylabs/oxylabs-ai-studio-py/tree/main/examples) folder for usage examples of each method. Each method has corresponding async version.
