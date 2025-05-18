import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")


def get_news(coin_name):
    try:
        url = f"https://cryptopanic.com/api/v1/posts/?auth_token={API_KEY}&currencies={coin_name.lower()}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            return [{"title": item["title"], "published_at": item["published_at"]} for item in results]
        else:
            return [{"title": f"Failed to fetch news. Status code: {response.status_code}", "published_at": "N/A"}]

    except requests.exceptions.RequestException as e:
        return [{"title": f"Error fetching news: {e}", "published_at": "N/A"}]


def get_price(token_symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={token_symbol.upper()}USDT"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data.get("price", "Unknown")
        else:
            return "Unknown"

    except requests.exceptions.RequestException as e:
        return f"Error fetching price: {e}"


def get_market_data(token_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{token_id.lower()}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return {
                "market_cap": data["market_data"]["market_cap"].get("usd", "Unknown"),
                "rank": data.get("market_cap_rank", "Unknown")
            }
        else:
            return {
                "market_cap": "Unknown",
                "rank": "Unknown"
            }

    except requests.exceptions.RequestException as e:
        return {
            "market_cap": f"Error: {e}",
            "rank": "Unknown"
        }
