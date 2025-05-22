import time
import streamlit as st
import logging
import requests
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple configurations
class SimpleConfig:
    def __init__(self):
        self.OLLAMA_BASE = "http://127.0.0.1:11434"
        self.REQUEST_TIMEOUT = 15  # Increased timeout
        self.MAX_RETRIES = 2  # Reduced retries for faster feedback

# Simple data fetcher with better error handling
class SimpleDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'AI-Crypto-Assistant/2.0'})
    
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """Get price from Binance API"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {"symbol": f"{symbol.upper()}USDT"}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "price": float(data.get("lastPrice", 0)),
                "change_24h": float(data.get("priceChangePercent", 0)),
                "volume": float(data.get("volume", 0)),
                "high": float(data.get("highPrice", 0)),
                "low": float(data.get("lowPrice", 0)),
                "source": "Binance",
                "status": "success"
            }
        except Exception as e:
            logger.warning(f"Binance API failed: {e}")
            return self._get_fallback_price_data()
    
    def get_market_data(self, coin_id: str) -> Dict[str, Any]:
        """Get market data from CoinGecko API"""
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": coin_id.lower(),
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_change": "true",
                "include_24hr_vol": "true"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if coin_id.lower() in data:
                coin_data = data[coin_id.lower()]
                return {
                    "price": coin_data.get("usd", 0),
                    "market_cap": coin_data.get("usd_market_cap", 0),
                    "volume_24h": coin_data.get("usd_24h_vol", 0),
                    "change_24h": coin_data.get("usd_24h_change", 0),
                    "source": "CoinGecko",
                    "status": "success"
                }
        except Exception as e:
            logger.warning(f"CoinGecko API failed: {e}")
        
        return self._get_fallback_market_data()
    
    def get_news(self, coin_name: str) -> list:
        """Get news - with graceful fallback if API fails"""
        try:
            # For now, return a placeholder since CryptoPanic is having issues
            return [
                {
                    "title": f"CryptoPanic API is currently experiencing issues (502 errors)",
                    "published_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "System Notice",
                    "status": "api_down"
                },
                {
                    "title": f"News for {coin_name} is temporarily unavailable",
                    "published_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "source": "System Notice",
                    "status": "fallback"
                }
            ]
        except Exception as e:
            logger.warning(f"News fetch failed: {e}")
            return []
    
    def _get_fallback_price_data(self):
        return {
            "price": 0,
            "change_24h": 0,
            "volume": 0,
            "high": 0,
            "low": 0,
            "source": "Unavailable",
            "status": "error"
        }
    
    def _get_fallback_market_data(self):
        return {
            "price": 0,
            "market_cap": 0,
            "volume_24h": 0,
            "change_24h": 0,
            "source": "Unavailable",
            "status": "error"
        }

# Simple response generator with better Ollama handling
class SimpleResponseGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def test_ollama_connection(self) -> bool:
        """Test if Ollama is accessible"""
        try:
            response = self.session.get("http://127.0.0.1:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_response(self, prompt: str, model: str = "llama2") -> str:
        """Generate response with better error handling"""
        # First test connection
        if not self.test_ollama_connection():
            return self._get_connection_error_response()
        
        try:
            # Try the generate endpoint
            url = "http://127.0.0.1:11434/api/generate"
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 300  # Reduced for faster response
                }
            }
            
            response = self.session.post(url, json=data, timeout=45)  # Increased timeout
            response.raise_for_status()
            result = response.json()
            
            generated_text = result.get("response", "")
            if generated_text:
                return generated_text
            else:
                return self._get_empty_response_error()
                
        except requests.exceptions.Timeout:
            return self._get_timeout_error_response()
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return self._get_generation_error_response(str(e))
    
    def _get_connection_error_response(self):
        return """
🔌 **Ollama Connection Error**

Не удается подключиться к Ollama серверу. Проверьте:

1. **Ollama запущен?**
   ```bash
   ollama serve
   ```

2. **Модель загружена?**
   ```bash
   ollama pull llama2
   ```

3. **Порт свободен?**
   - Ollama должен работать на порту 11434
   - Проверьте: http://localhost:11434

**Временное решение:** Используйте данные выше для анализа.
        """.strip()
    
    def _get_timeout_error_response(self):
        return """
⏱️ **Ollama Timeout Error**

Модель слишком долго генерирует ответ. Попробуйте:

1. **Использовать более быструю модель:**
   ```bash
   ollama pull llama2:7b-chat
   ```

2. **Перезапустить Ollama:**
   ```bash
   # Ctrl+C чтобы остановить
   ollama serve
   ```

3. **Проверить загрузку системы** - возможно, модель перегружена

**Данные выше показывают текущее состояние рынка.**
        """.strip()
    
    def _get_empty_response_error(self):
        return "⚠️ Ollama вернул пустой ответ. Попробуйте другую модель или перезапустите сервер."
    
    def _get_generation_error_response(self, error):
        return f"""
❌ **Ошибка генерации AI ответа**

Техническая ошибка: {error}

**Решения:**
1. Перезапустить Ollama: `ollama serve`
2. Проверить доступные модели: `ollama list`
3. Загрузить базовую модель: `ollama pull llama2`

**Рыночные данные выше остаются актуальными.**
        """.strip()

# Simple token extraction
def extract_token_info(query: str) -> Optional[Dict[str, str]]:
    """Simple token extraction"""
    query_lower = query.lower()
    
    # Simple mapping for major cryptocurrencies
    token_map = {
        "bitcoin": {"name": "Bitcoin", "symbol": "BTC", "id": "bitcoin"},
        "btc": {"name": "Bitcoin", "symbol": "BTC", "id": "bitcoin"},
        "ethereum": {"name": "Ethereum", "symbol": "ETH", "id": "ethereum"},
        "eth": {"name": "Ethereum", "symbol": "ETH", "id": "ethereum"},
        "binance": {"name": "Binance Coin", "symbol": "BNB", "id": "binancecoin"},
        "bnb": {"name": "Binance Coin", "symbol": "BNB", "id": "binancecoin"},
        "cardano": {"name": "Cardano", "symbol": "ADA", "id": "cardano"},
        "ada": {"name": "Cardano", "symbol": "ADA", "id": "cardano"},
        "solana": {"name": "Solana", "symbol": "SOL", "id": "solana"},
        "sol": {"name": "Solana", "symbol": "SOL", "id": "solana"},
        "dogecoin": {"name": "Dogecoin", "symbol": "DOGE", "id": "dogecoin"},
        "doge": {"name": "Dogecoin", "symbol": "DOGE", "id": "dogecoin"},
        "polkadot": {"name": "Polkadot", "symbol": "DOT", "id": "polkadot"},
        "dot": {"name": "Polkadot", "symbol": "DOT", "id": "polkadot"},
        "chainlink": {"name": "Chainlink", "symbol": "LINK", "id": "chainlink"},
        "link": {"name": "Chainlink", "symbol": "LINK", "id": "chainlink"},
    }
    
    # Check for direct matches
    for token, info in token_map.items():
        if token in query_lower:
            return info
    
    # Fallback to Bitcoin if nothing found
    return {"name": "Bitcoin", "symbol": "BTC", "id": "bitcoin"}

# Utility functions
def format_currency(value):
    """Format currency values"""
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    else:
        return f"{value:.2f}"

def main():
    st.set_page_config(
        page_title="🧠 AI Crypto Assistant (Debug Mode)",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("🧠 AI Crypto Assistant - Debug Mode")
    st.markdown("*Enhanced error handling and diagnostics*")
    
    # Initialize components
    config = SimpleConfig()
    data_fetcher = SimpleDataFetcher()
    response_generator = SimpleResponseGenerator()
    
    # Sidebar with diagnostics
    with st.sidebar:
        st.header("🔧 System Status")
        
        # Test Ollama connection
        ollama_status = response_generator.test_ollama_connection()
        if ollama_status:
            st.success("✅ Ollama: Connected")
        else:
            st.error("❌ Ollama: Disconnected")
            st.markdown("**Fix:** Run `ollama serve` in terminal")
        
        # Test APIs
        st.markdown("**API Status:**")
        try:
            test_response = requests.get("https://api.binance.com/api/v3/ping", timeout=5)
            if test_response.status_code == 200:
                st.success("✅ Binance API")
            else:
                st.warning("⚠️ Binance API")
        except:
            st.error("❌ Binance API")
        
        try:
            test_response = requests.get("https://api.coingecko.com/api/v3/ping", timeout=5)
            if test_response.status_code == 200:
                st.success("✅ CoinGecko API")
            else:
                st.warning("⚠️ CoinGecko API")
        except:
            st.error("❌ CoinGecko API")
        
        st.error("❌ CryptoPanic API (Known issue)")
        
        st.markdown("---")
        st.markdown("**Available Models:**")
        try:
            response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models[:5]:  # Show first 5
                    st.text(f"• {model['name']}")
            else:
                st.text("Cannot fetch models")
        except:
            st.text("Ollama not accessible")
    
    # Main interface
    query = st.text_input(
        "Ask about a cryptocurrency",
        placeholder="e.g., 'Tell me about Bitcoin'",
        help="Enter any cryptocurrency name"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_button = st.button("🔍 Analyze", type="primary")
    with col2:
        if st.button("🔄 Test Ollama"):
            with st.spinner("Testing Ollama connection..."):
                if response_generator.test_ollama_connection():
                    st.success("✅ Ollama is working!")
                    # Test generation
                    test_response = response_generator.generate_response(
                        "Say 'Hello, I am working!' in Russian",
                        "llama2"
                    )
                    st.write("**Test Response:**", test_response)
                else:
                    st.error("❌ Cannot connect to Ollama")
    
    if query and analyze_button:
        with st.spinner("Analyzing..."):
            # Extract token
            token_info = extract_token_info(query)
            st.success(f"🎯 Analyzing: **{token_info['name']} ({token_info['symbol']})**")
            
            # Create progress
            progress_bar = st.progress(0)
            
            # Fetch data
            progress_bar.progress(25)
            st.write("📊 Fetching price data...")
            price_data = data_fetcher.get_price(token_info['symbol'])
            
            progress_bar.progress(50)
            st.write("📈 Fetching market data...")
            market_data = data_fetcher.get_market_data(token_info['id'])
            
            progress_bar.progress(75)
            st.write("📰 Fetching news...")
            news_data = data_fetcher.get_news(token_info['name'])
            
            progress_bar.progress(100)
            
            # Display data
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                price = price_data.get('price', 0)
                st.metric("Price (USD)", f"${price:.2f}" if price > 0 else "N/A")
            
            with col2:
                change = price_data.get('change_24h', 0)
                st.metric("24h Change", f"{change:.2f}%" if change != 0 else "N/A")
            
            with col3:
                market_cap = market_data.get('market_cap', 0)
                st.metric("Market Cap", f"${format_currency(market_cap)}" if market_cap > 0 else "N/A")
            
            with col4:
                volume = price_data.get('volume', 0)
                st.metric("24h Volume", f"{format_currency(volume)}" if volume > 0 else "N/A")
            
            # News section
            st.subheader("📰 Latest News")
            for article in news_data[:3]:
                st.write(f"• **{article['title']}** _{article['source']}_")
            
            # AI Analysis
            st.subheader("🤖 AI Analysis")
            
            # Create prompt
            prompt = f"""
Проанализируй криптовалюту {token_info['name']} ({token_info['symbol']}) на основе данных:

Цена: ${price_data.get('price', 'N/A')}
Изменение за 24ч: {price_data.get('change_24h', 'N/A')}%
Рыночная капитализация: ${market_data.get('market_cap', 'N/A')}

Дай краткий анализ (2-3 абзаца) на русском языке. Включи:
1. Текущее состояние
2. Краткий прогноз
3. Основные факторы влияния

Будь объективным и не давай финансовых советов.
            """
            
            ai_response = response_generator.generate_response(prompt)
            st.markdown(ai_response)
            
            # Clear progress
            progress_bar.empty()

if __name__ == "__main__":
    main()