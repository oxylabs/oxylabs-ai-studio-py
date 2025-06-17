from pydantic import BaseModel
from oxylabs_ai_studio.apps.ai_scraper import AiScraper

scraper = AiScraper(api_key="<API_KEY>")

class Game(BaseModel):
    title: str
    genre: list[str]
    developer: str
    platform: str
    game_type: str
    description: str
    price: str
    availability: str

url = "https://sandbox.oxylabs.io/products/1"
result = scraper.scrape(
    url=url,
    output_format="json",
    schema=Game.model_json_schema(),
    render_javascript=False,
)
print(result)



