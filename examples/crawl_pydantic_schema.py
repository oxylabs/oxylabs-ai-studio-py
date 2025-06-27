from pydantic import BaseModel, Field
from oxylabs_ai_studio.apps.ai_crawler import AiCrawler


crawler = AiCrawler(api_key="<API_KEY>")

class ProxyPlan(BaseModel):
    name: str = Field(description="The name of the proxy plan")
    price: str = Field(description="The price of the proxy plan")
    features: list[str] = Field(description="The features of the proxy plan")


class ProxyPlans(BaseModel):
    proxy_plans: list[ProxyPlan] = Field(description="The proxy plans")


url = "https://oxylabs.io/"
result = crawler.crawl(
    url=url,
    user_prompt="Find all pages with proxy products pricing",
    output_format="json",
    schema=ProxyPlans.model_json_schema(),
    render_javascript=False,
)
print("Results:\n")
for item in result.data:
    print(item, "\n")
