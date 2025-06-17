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
