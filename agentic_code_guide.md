# Oxylabs AI Studio Python SDK Agentic Code Guide

## Installation

```bash
pip install oxylabs-ai-studio
```

## Best Practices for Implementation

- Install latest version of oxylabs-ai-studio.
- Incorporate Rate Limiting: Ensure your implementation respects rate limits associated with your 
    purchased plan to prevent service disruptions or overuse.
- Implement a Robust Retry Mechanism: Introduce a retry logic for handling failed requests, but 
    include a limit to the number of retries to avoid infinite loops or excessive API calls.

## Browser-Agent app

### What It Is Good For

A browser automation tool capable of controlling a browser to perform actions such as 
clicking, scrolling, and navigation. The tool takes a textual prompt as input to execute 
these actions.

### Python interface

#### Sync interface

```python
from oxylabs_ai_studio.apps.browser_agent import BrowserAgent

browser_agent = BrowserAgent(api_key="<API_KEY>")

prompt = "Find if there is game 'super mario odyssey' in the store."
url = "https://sandbox.oxylabs.io/"
result = browser_agent.run(
    url=url,
    user_prompt=prompt,
    output_format="json",
    schema={"type": "object", "properties": {"page_url": {"type": "string"}}, "required": []},
)
print(result.data)
```

#### Async interface

```python
import asyncio
from oxylabs_ai_studio.apps.browser_agent import BrowserAgent

browser_agent = BrowserAgent(api_key="<API_KEY>")

async def main():
    prompt = "Find if there is game 'super mario odyssey' in the store."
    url = "https://sandbox.oxylabs.io/"
    result = await browser_agent.run_async(
        url=url,
        user_prompt=prompt,
        output_format="json",
        schema={"type": "object", "properties": {"page_url": {"type": "string"}}, "required": []},
    )
    print(result.data)

if __name__ == "__main__":
    asyncio.run(main())
```

Parameters:

- url (str): Target URL to scrape (required).
- user_prompt (str): User prompt to perform browser actions. Mention task or actions instead of what you like to extract from it. (required).
- output_format (Literal["json", "markdown"]): Output format (default: "markdown").
- schema (dict | None): OpenAPI schema for structured extraction (required if output_format is "json").

Output (result):

- Python classes:

    ```python
    class DataModel(BaseModel):
        type: Literal["json", "markdown", "html", "screenshot", "csv"]
        content: dict[str, Any] | str | None

    class BrowserAgentJob(BaseModel):
        run_id: str
        message: str | None = None
        data: DataModel | None = None
    ```

## AI-Scraper app

### What It Is Good For

A tool designed to scrape website content and return it either as Markdown or structured JSON. 
When opting for JSON output, the user must provide a valid JSON schema for the expected structure.

### Python interface

#### Sync interface

```python
from oxylabs_ai_studio.apps.ai_scraper import AiScraper

scraper = AiScraper(api_key="<API_KEY>")

url = "https://sandbox.oxylabs.io/products/3"
result = scraper.scrape(
    url=url,
    output_format="json",
    schema={"type": "object", "properties": {"price": {"type": "string"}}, "required": []},
    render_javascript=False,
)
print(result)
```

#### Async interface

```python
import asyncio
from oxylabs_ai_studio.apps.ai_scraper import AiScraper

scraper = AiScraper(api_key="<API_KEY>")

async def main():
    url = "https://sandbox.oxylabs.io/products/3"
    result = await scraper.scrape_async(
        url=url,
        output_format="json",
        schema={"type": "object", "properties": {"price": {"type": "string"}}, "required": []},
        render_javascript=False,
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

Parameters:

- url (str): Target URL to scrape (required)
- output_format (Literal["json", "markdown", "csv", "screenshot"]): Output format (default: "markdown")
- schema (dict | None): OpenAPI schema for structured extraction (required if output_format is "json")
- render_javascript (bool): Render JavaScript (default: False)
- geo_location (str): proxy location in ISO2 format.

Output (result):

- Python classes:

    ```python
    class AiScraperJob(BaseModel):
        run_id: str
        message: str | None = None
        data: str | dict | None
    ```

    If output_format is "json", data will be a dictionary.
    If output_format is "markdown", data will be a string.
    If output_format is "csv", data will be a string formatted in a form of csv.
    If output_format is "screenshot", data will be a string.


## Use Cases Examples

### E-commerce Product Scraping

- Task: Locate the category page of a specific domain, extract all product data from the category, and gather detailed information from each product page.
- Proposed Workflow:
    - Use the Browser-Agent app to identify the category page URL and all pagination URLs within that category in a single action.
        Define a JSON schema to return the pagination URLs. Example:
        ```json
        {
        "type": "object",
        "properties": {
            "paginationUrls": {
                "type": "array",
                "description": "Return all URLs from first to last page in category pagination. If you noticed there are missing URLs, because category page does not list them all, create them to match existing ones.",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": []
        }
        ```
    - Use the Ai-Scraper app to extract all product URLs from the pagination pages in the category.
    - Use the Ai-Scraper app again to extract detailed data from each product page by defining an appropriate JSON schema.
