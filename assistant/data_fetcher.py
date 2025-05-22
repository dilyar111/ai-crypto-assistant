import requests
import time
import logging
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import streamlit as st

logger = logging.getLogger(__name__)

class DataFetcher:
    """Enhanced data fetcher with improved CryptoPanic API handling"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-Crypto-Assistant/2.0'
        })
    
    def _make_request(self, url: str, params: Dict = None, max_retries: int = None) -> Optional[Dict]:
        """Make HTTP request with retry logic"""
        max_retries = max_retries or self.config.MAX_RETRIES
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} attempts failed for {url}")
                    return None
                time.sleep(self.config.RETRY_DELAY * (attempt + 1))
        
        return None
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_news(_self, coin_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch cryptocurrency news from CryptoPanic with improved error handling"""
        if not _self.config.api_keys.CRYPTOPANIC:
            return _self._get_no_api_key_news(coin_name)
        
        # Try multiple CryptoPanic endpoints and parameters
        endpoints_to_try = [
            # Method 1: Standard posts endpoint
            {
                "url": "https://cryptopanic.com/api/v1/posts/",
                "params": {
                    "auth_token": _self.config.api_keys.CRYPTOPANIC,
                    "currencies": coin_name.lower(),
                    "public": "true"
                }
            },
            # Method 2: Without filter parameter
            {
                "url": "https://cryptopanic.com/api/v1/posts/",
                "params": {
                    "auth_token": _self.config.api_keys.CRYPTOPANIC,
                    "currencies": coin_name.lower()
                }
            },
            # Method 3: Different currency format
            {
                "url": "https://cryptopanic.com/api/v1/posts/",
                "params": {
                    "auth_token": _self.config.api_keys.CRYPTOPANIC,
                    "currencies": _self._get_currency_code(coin_name),
                    "public": "true"
                }
            },
            # Method 4: General crypto news (fallback)
            {
                "url": "https://cryptopanic.com/api/v1/posts/",
                "params": {
                    "auth_token": _self.config.api_keys.CRYPTOPANIC,
                    "public": "true"
                }
            }
        ]
        
        for i, endpoint_config in enumerate(endpoints_to_try):
            try:
                logger.info(f"Trying CryptoPanic method {i+1}/4")
                data = _self._make_request(endpoint_config["url"], endpoint_config["params"])
                
                if data and "results" in data:
                    results = data.get("results", [])
                    if results:  # If we got results, process them
                        news_items = []
                        for item in results[:limit]:
                            # Filter for relevant news if we're using general endpoint
                            title = item.get("title", "").lower()
                            if i == 3:  # General news endpoint
                                if coin_name.lower() not in title and _self._get_currency_code(coin_name).lower() not in title:
                                    continue
                            
                            news_items.append({
                                "title": item.get("title", "No title"),
                                "published_at": item.get("published_at", "Unknown"),
                                "url": item.get("url", "#"),
                                "source": item.get("source", {}).get("title", "Unknown") if isinstance(item.get("source"), dict) else str(item.get("source", "Unknown")),
                                "kind": item.get("kind", "news"),
                                "votes": {
                                    "positive": item.get("votes", {}).get("positive", 0),
                                    "negative": item.get("votes", {}).get("negative", 0)
                                }
                            })
                        
                        if news_items:
                            logger.info(f"Successfully fetched {len(news_items)} news items using method {i+1}")
                            return news_items
                        elif i < 3:  # Continue trying if no relevant news found
                            continue
                    elif i < 3:  # Continue trying if no results
                        continue
                        
            except Exception as e:
                logger.warning(f"CryptoPanic method {i+1} failed: {e}")
                continue
        
        # If all methods fail, return informative fallback
        return _self._get_fallback_news(coin_name)
    
    def _get_currency_code(self, coin_name: str) -> str:
        """Convert coin name to currency code"""
        currency_map = {
            "bitcoin": "BTC",
            "ethereum": "ETH", 
            "binance": "BNB",
            "cardano": "ADA",
            "solana": "SOL",
            "dogecoin": "DOGE",
            "polkadot": "DOT",
            "chainlink": "LINK",
            "litecoin": "LTC",
            "polygon": "MATIC",
            "avalanche": "AVAX"
        }
        return currency_map.get(coin_name.lower(), coin_name.upper())
    
    def _get_no_api_key_news(self, coin_name: str) -> List[Dict[str, Any]]:
        """Return helpful message when no API key is configured"""
        return [
            {
                "title": f"CryptoPanic API key not configured for {coin_name} news",
                "published_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "url": "https://cryptopanic.com/developers/api/",
                "source": "Configuration Notice",
                "kind": "notice"
            },
            {
                "title": "Get a free API key at cryptopanic.com to enable news features",
                "published_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "url": "https://cryptopanic.com/developers/api/",
                "source": "Setup Guide",
                "kind": "info"
            }
        ]
    
    def _get_fallback_news(self, coin_name: str) -> List[Dict[str, Any]]:
        """Return informative fallback when API fails"""
        return [
            {
                "title": f"CryptoPanic API is temporarily unavailable for {coin_name} news",
                "published_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "url": "#",
                "source": "System Notice",
                "kind": "notice"
            },
            {
                "title": f"Price and market data for {coin_name} are still available from other sources",
                "published_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "url": "#",
                "source": "System Info",
                "kind": "info"
            },
            {
                "title": "News will automatically resume when CryptoPanic API is restored",
                "published_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "url": "#",
                "source": "Auto-Recovery",
                "kind": "info"
            }
        ]
    
    @st.cache_data(ttl=30)  # Cache for 30 seconds (price changes frequently)
    def get_price(_self, token_symbol: str) -> Dict[str, Any]:
        """Fetch current price from Binance"""
        try:
            # Try Binance first
            url = _self.config.get_binance_url("ticker/24hr")
            params = {"symbol": f"{token_symbol.upper()}USDT"}
            
            data = _self._make_request(url, params)
            if data:
                return {
                    "price": float(data.get("lastPrice", 0)),
                    "change_24h": float(data.get("priceChangePercent", 0)),
                    "volume_24h": float(data.get("volume", 0)),
                    "high_24h": float(data.get("highPrice", 0)),
                    "low_24h": float(data.get("lowPrice", 0)),
                    "source": "Binance"
                }
        except Exception as e:
            logger.warning(f"Binance price fetch failed: {e}")
        
        # Fallback to CoinGecko
        try:
            url = _self.config.get_coingecko_url(f"simple/price")
            params = {
                "ids": token_symbol.lower(),
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true"
            }
            
            data = _self._make_request(url, params)
            if data and token_symbol.lower() in data:
                coin_data = data[token_symbol.lower()]
                return {
                    "price": coin_data.get("usd", 0),
                    "change_24h": coin_data.get("usd_24h_change", 0),
                    "volume_24h": coin_data.get("usd_24h_vol", 0),
                    "source": "CoinGecko"
                }
        except Exception as e:
            logger.warning(f"CoinGecko price fetch failed: {e}")
        
        return {
            "price": 0,
            "change_24h": 0,
            "volume_24h": 0,
            "source": "Error"
        }
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_market_data(_self, token_id: str) -> Dict[str, Any]:
        """Fetch comprehensive market data from CoinGecko"""
        url = _self.config.get_coingecko_url(f"coins/{token_id.lower()}")
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "true",
            "developer_data": "false",
            "sparkline": "false"
        }
        
        data = _self._make_request(url, params)
        if not data:
            return _self._get_fallback_market_data()
        
        try:
            market_data = data.get("market_data", {})
            return {
                "market_cap": market_data.get("market_cap", {}).get("usd", 0),
                "rank": data.get("market_cap_rank", 0),
                "total_volume": market_data.get("total_volume", {}).get("usd", 0),
                "circulating_supply": market_data.get("circulating_supply", 0),
                "total_supply": market_data.get("total_supply", 0),
                "max_supply": market_data.get("max_supply", 0),
                "price_change_24h": market_data.get("price_change_percentage_24h", 0),
                "price_change_7d": market_data.get("price_change_percentage_7d", 0),
                "price_change_30d": market_data.get("price_change_percentage_30d", 0),
                "ath": market_data.get("ath", {}).get("usd", 0),
                "atl": market_data.get("atl", {}).get("usd", 0),
                "last_updated": market_data.get("last_updated", "Unknown")
            }
        except Exception as e:
            logger.error(f"Error parsing market data: {e}")
            return _self._get_fallback_market_data()
    
    def _get_fallback_market_data(self) -> Dict[str, Any]:
        """Return fallback market data when API fails"""
        return {
            "market_cap": 0,
            "rank": 0,
            "total_volume": 0,
            "circulating_supply": 0,
            "total_supply": 0,
            "max_supply": 0,
            "price_change_24h": 0,
            "price_change_7d": 0,
            "price_change_30d": 0,
            "ath": 0,
            "atl": 0,
            "last_updated": "Unknown"
        }
    
    def get_comprehensive_data(self, token_info: Dict[str, str]) -> Dict[str, Any]:
        """Fetch all data concurrently for better performance"""
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all requests concurrently
            future_to_data_type = {
                executor.submit(self.get_news, token_info['name']): 'news',
                executor.submit(self.get_price, token_info['symbol']): 'price',
                executor.submit(self.get_market_data, token_info['id']): 'market'
            }
            
            results = {}
            for future in as_completed(future_to_data_type):
                data_type = future_to_data_type[future]
                try:
                    results[data_type] = future.result()
                except Exception as e:
                    logger.error(f"Error fetching {data_type} data: {e}")
                    results[data_type] = None
            
            return results