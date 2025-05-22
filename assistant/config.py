import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class APIEndpoints:
    """API endpoint configurations"""
    CRYPTOPANIC_BASE = "https://cryptopanic.com/api/v1"
    BINANCE_BASE = "https://api.binance.com/api/v3"
    COINGECKO_BASE = "https://api.coingecko.com/api/v3"
    OLLAMA_BASE = "http://127.0.0.1:11434"

@dataclass
class APIKeys:
    """API key configurations"""
    CRYPTOPANIC: Optional[str] = None
    BINANCE: Optional[str] = None
    COINGECKO: Optional[str] = None

@dataclass
class ModelSettings:
    """Model configuration settings"""
    DEFAULT_MODEL = "llama2"
    MAX_TOKENS = 500
    TEMPERATURE = 0.7
    TOP_P = 0.9
    
class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.endpoints = APIEndpoints()
        self.api_keys = APIKeys(
            CRYPTOPANIC=os.getenv("CRYPTOPANIC_API_KEY") or os.getenv("API_KEY"),
            BINANCE=os.getenv("BINANCE_API_KEY"),
            COINGECKO=os.getenv("COINGECKO_API_KEY")
        )
        self.model_settings = ModelSettings()
        
        # Request settings
        self.REQUEST_TIMEOUT = 10
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 1
        
        # Cache settings
        self.CACHE_TTL = 300  # 5 minutes
        
        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration settings"""
        if not self.api_keys.CRYPTOPANIC:
            print("⚠️ Warning: CRYPTOPANIC_API_KEY not found. News fetching may be limited.")
        
        # Check if Ollama is accessible
        try:
            import requests
            response = requests.get(f"{self.endpoints.OLLAMA_BASE}/api/tags", timeout=5)
            if response.status_code != 200:
                print("⚠️ Warning: Ollama server may not be running.")
        except Exception:
            print("⚠️ Warning: Cannot connect to Ollama server.")
    
    def get_ollama_url(self, endpoint: str = "") -> str:
        """Get full Ollama URL"""
        return f"{self.endpoints.OLLAMA_BASE}/{endpoint}".rstrip("/")
    
    def get_cryptopanic_url(self, endpoint: str = "") -> str:
        """Get full CryptoPanic URL"""
        return f"{self.endpoints.CRYPTOPANIC_BASE}/{endpoint}".rstrip("/")
    
    def get_binance_url(self, endpoint: str = "") -> str:
        """Get full Binance URL"""
        return f"{self.endpoints.BINANCE_BASE}/{endpoint}".rstrip("/")
    
    def get_coingecko_url(self, endpoint: str = "") -> str:
        """Get full CoinGecko URL"""
        return f"{self.endpoints.COINGECKO_BASE}/{endpoint}".rstrip("/")

# Global config instance
config = Config()