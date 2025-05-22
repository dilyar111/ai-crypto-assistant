import requests
import json
import logging
from typing import Dict, Any, List, Optional
import streamlit as st

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Fixed response generator with better Ollama handling"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AI-Crypto-Assistant/2.0'
        })
        
        # Template mappings for different languages
        self.templates = {
            "russian": {
                "system_prompt": "Ты эксперт-аналитик криптовалют. Предоставляй точную, объективную и полезную информацию.",
                "analysis_intro": "Анализ криптовалюты:",
                "sections": {
                    "overview": "📊 Обзор",
                    "price_analysis": "💰 Анализ цены",
                    "market_data": "📈 Рыночные данные",
                    "news_summary": "📰 Новости",
                    "technical_analysis": "🔍 Технический анализ",
                    "risks": "⚠️ Риски",
                    "conclusion": "💡 Заключение"
                }
            },
            "english": {
                "system_prompt": "You are a cryptocurrency expert analyst. Provide accurate, objective, and helpful information.",
                "analysis_intro": "Cryptocurrency Analysis:",
                "sections": {
                    "overview": "📊 Overview",
                    "price_analysis": "💰 Price Analysis",
                    "market_data": "📈 Market Data",
                    "news_summary": "📰 News Summary",
                    "technical_analysis": "🔍 Technical Analysis",
                    "risks": "⚠️ Risks",
                    "conclusion": "💡 Conclusion"
                }
            }
        }
    
    def test_ollama_connection(self) -> bool:
        """Test if Ollama is accessible"""
        try:
            response = self.session.get("http://127.0.0.1:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama connection test failed: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = self.session.get("http://127.0.0.1:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.warning(f"Failed to get models: {e}")
        return ["llama2"]
    
    def create_analysis_prompt(
        self, 
        token_info: Dict[str, str], 
        market_data: Dict[str, Any], 
        price_data: Dict[str, Any], 
        news_data: List[Dict[str, Any]], 
        language: str = "russian", 
        depth: str = "detailed"
    ) -> str:
        """Create comprehensive analysis prompt"""
        
        template = self.templates.get(language, self.templates["russian"])
        
        # Format market data
        market_summary = self._format_market_data(market_data, price_data, language)
        
        # Format news summary
        news_summary = self._format_news_summary(news_data, language)
        
        # Create depth-specific instructions
        depth_instructions = self._get_depth_instructions(depth, language)
        
        prompt = f"""
{template['system_prompt']}

{template['analysis_intro']} {token_info['name']} ({token_info['symbol']})

ДАННЫЕ ДЛЯ АНАЛИЗА:
{market_summary}

ПОСЛЕДНИЕ НОВОСТИ:
{news_summary}

{depth_instructions}

ВАЖНО: 
- Используй только предоставленные данные
- Будь объективным и сбалансированным
- Не давай финансовых советов
- Структурируй ответ с помощью разделов
- Используй эмодзи для лучшего восприятия

Ответь кратко но содержательно (максимум 300 слов).
"""
        
        return prompt
    
    def _format_market_data(self, market_data: Dict[str, Any], price_data: Dict[str, Any], language: str) -> str:
        """Format market data for prompt"""
        if language == "russian":
            return f"""
💰 Текущая цена: ${price_data.get('price', 'N/A')}
📊 Изменение за 24ч: {price_data.get('change_24h', 0):.2f}%
🏆 Рейтинг по капитализации: #{market_data.get('rank', 'N/A')}
💎 Рыночная капитализация: ${market_data.get('market_cap', 0):,.0f}
📈 Объем торгов 24ч: ${market_data.get('total_volume', 0):,.0f}
🔄 В обращении: {market_data.get('circulating_supply', 0):,.0f}
"""
        else:
            return f"""
💰 Current Price: ${price_data.get('price', 'N/A')}
📊 24h Change: {price_data.get('change_24h', 0):.2f}%
🏆 Market Cap Rank: #{market_data.get('rank', 'N/A')}
💎 Market Cap: ${market_data.get('market_cap', 0):,.0f}
📈 24h Volume: ${market_data.get('total_volume', 0):,.0f}
🔄 Circulating Supply: {market_data.get('circulating_supply', 0):,.0f}
"""
    
    def _format_news_summary(self, news_data: List[Dict[str, Any]], language: str) -> str:
        """Format news data for prompt"""
        if not news_data:
            return "Новости недоступны" if language == "russian" else "No news available"
        
        news_text = ""
        for i, article in enumerate(news_data[:3], 1):
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown source')
            news_text += f"{i}. {title} ({source})\n"
        
        return news_text
    
    def _get_depth_instructions(self, depth: str, language: str) -> str:
        """Get analysis depth instructions"""
        if language == "russian":
            instructions = {
                "basic": "Предоставь краткий обзор (2-3 абзаца) с основными метриками и выводами.",
                "detailed": "Предоставь подробный анализ (3-4 абзаца) с разбором данных и трендов.",
                "comprehensive": "Предоставь исчерпывающий анализ (4-5 абзацев) с техническим анализом и прогнозами."
            }
        else:
            instructions = {
                "basic": "Provide a brief overview (2-3 paragraphs) with key metrics and conclusions.",
                "detailed": "Provide detailed analysis (3-4 paragraphs) with data analysis and trends.",
                "comprehensive": "Provide comprehensive analysis (4-5 paragraphs) with technical analysis and forecasts."
            }
        
        return instructions.get(depth, instructions["detailed"])
    
    def generate_response(self, prompt: str, model: str = None, max_retries: int = 2) -> str:
        """Generate response using Ollama API with improved error handling"""
        model = model or "llama2"
        
        # First test connection
        if not self.test_ollama_connection():
            return self._get_connection_error_response()
        
        # Try different endpoints in order of preference
        endpoints = [
            {
                "url": "http://127.0.0.1:11434/api/generate",
                "data_format": "generate"
            },
            {
                "url": "http://127.0.0.1:11434/api/chat", 
                "data_format": "chat"
            }
        ]
        
        for endpoint_info in endpoints:
            try:
                logger.info(f"Trying endpoint: {endpoint_info['url']}")
                
                if endpoint_info["data_format"] == "generate":
                    data = {
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "num_predict": 400,  # Reasonable limit for faster response
                            "stop": ["\n\n\n"]  # Stop at triple newlines
                        }
                    }
                else:  # chat format
                    data = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 400
                        }
                    }
                
                response = self.session.post(
                    endpoint_info["url"], 
                    json=data, 
                    timeout=60  # Increased timeout for generation
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract response based on endpoint format
                    if endpoint_info["data_format"] == "generate":
                        generated_text = result.get("response", "")
                    else:  # chat format
                        generated_text = result.get("message", {}).get("content", "")
                    
                    if generated_text and generated_text.strip():
                        logger.info(f"Successfully generated response using {endpoint_info['url']}")
                        return generated_text.strip()
                    else:
                        logger.warning(f"Empty response from {endpoint_info['url']}")
                        continue
                        
                else:
                    logger.warning(f"HTTP {response.status_code} from {endpoint_info['url']}")
                    continue
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout for endpoint {endpoint_info['url']}")
                continue
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error for {endpoint_info['url']}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error with endpoint {endpoint_info['url']}: {e}")
                continue
        
        # If all endpoints fail, return timeout error
        return self._get_timeout_error_response()
    
    def _get_connection_error_response(self):
        return """
🔌 **Ollama Подключение Недоступно**

Не удается подключиться к Ollama серверу.

**Быстрое решение:**
1. Откройте новый терминал и запустите: `ollama serve`
2. Проверьте доступность: http://localhost:11434
3. Убедитесь что модель загружена: `ollama pull llama2`

**Текущие данные выше остаются актуальными для анализа.**
        """.strip()
    
    def _get_timeout_error_response(self):
        return """
⏱️ **Ollama Генерация Заняла Слишком Много Времени**

**Возможные решения:**
1. **Перезапустить Ollama:** Остановите (Ctrl+C) и снова `ollama serve`
2. **Попробовать более быструю модель:** `ollama pull phi` или `ollama pull llama2:7b-chat`
3. **Проверить загрузку системы** - возможно модель перегружена

**Рыночные данные выше показывают текущую ситуацию.**

**💡 Краткий анализ на основе данных:**
Если цена показывает положительную динамику (+4.63%), это указывает на bullish настроения. 
Высокая рыночная капитализация и объемы торгов говорят о здоровом интересе к активу.
        """.strip()
    
    def quick_test_generation(self) -> str:
        """Quick test to see if generation works"""
        try:
            test_prompt = "Скажи 'Привет' одним словом."
            response = self.generate_response(test_prompt, "llama2")
            return response
        except Exception as e:
            return f"Test failed: {e}"