import re
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TokenInfo:
    """Token information structure"""
    name: str
    symbol: str
    id: str  # CoinGecko ID
    aliases: List[str] = None

class QueryHandler:
    """Enhanced query handler with comprehensive token recognition"""
    
    def __init__(self):
        self.token_mapping = self._initialize_token_mapping()
        self.query_patterns = self._initialize_query_patterns()
    
    def _initialize_token_mapping(self) -> Dict[str, TokenInfo]:
        """Initialize comprehensive token mapping"""
        return {
            # Major cryptocurrencies
            "bitcoin": TokenInfo("Bitcoin", "BTC", "bitcoin", ["btc", "bitcoin"]),
            "btc": TokenInfo("Bitcoin", "BTC", "bitcoin", ["btc", "bitcoin"]),
            
            "ethereum": TokenInfo("Ethereum", "ETH", "ethereum", ["eth", "ethereum", "ether"]),
            "eth": TokenInfo("Ethereum", "ETH", "ethereum", ["eth", "ethereum", "ether"]),
            "ether": TokenInfo("Ethereum", "ETH", "ethereum", ["eth", "ethereum", "ether"]),
            
            "binance": TokenInfo("Binance Coin", "BNB", "binancecoin", ["bnb", "binance coin"]),
            "bnb": TokenInfo("Binance Coin", "BNB", "binancecoin", ["bnb", "binance coin"]),
            
            "cardano": TokenInfo("Cardano", "ADA", "cardano", ["ada", "cardano"]),
            "ada": TokenInfo("Cardano", "ADA", "cardano", ["ada", "cardano"]),
            
            "solana": TokenInfo("Solana", "SOL", "solana", ["sol", "solana"]),
            "sol": TokenInfo("Solana", "SOL", "solana", ["sol", "solana"]),
            
            "polkadot": TokenInfo("Polkadot", "DOT", "polkadot", ["dot", "polkadot"]),
            "dot": TokenInfo("Polkadot", "DOT", "polkadot", ["dot", "polkadot"]),
            
            "chainlink": TokenInfo("Chainlink", "LINK", "chainlink", ["link", "chainlink"]),
            "link": TokenInfo("Chainlink", "LINK", "chainlink", ["link", "chainlink"]),
            
            "litecoin": TokenInfo("Litecoin", "LTC", "litecoin", ["ltc", "litecoin"]),
            "ltc": TokenInfo("Litecoin", "LTC", "litecoin", ["ltc", "litecoin"]),
            
            "polygon": TokenInfo("Polygon", "MATIC", "matic-network", ["matic", "polygon"]),
            "matic": TokenInfo("Polygon", "MATIC", "matic-network", ["matic", "polygon"]),
            
            "avalanche": TokenInfo("Avalanche", "AVAX", "avalanche-2", ["avax", "avalanche"]),
            "avax": TokenInfo("Avalanche", "AVAX", "avalanche-2", ["avax", "avalanche"]),
            
            "dogecoin": TokenInfo("Dogecoin", "DOGE", "dogecoin", ["doge", "dogecoin"]),
            "doge": TokenInfo("Dogecoin", "DOGE", "dogecoin", ["doge", "dogecoin"]),
            
            "shiba": TokenInfo("Shiba Inu", "SHIB", "shiba-inu", ["shib", "shiba inu", "shiba"]),
            "shib": TokenInfo("Shiba Inu", "SHIB", "shiba-inu", ["shib", "shiba inu", "shiba"]),
            
            "ripple": TokenInfo("XRP", "XRP", "ripple", ["xrp", "ripple"]),
            "xrp": TokenInfo("XRP", "XRP", "ripple", ["xrp", "ripple"]),
            
            # Stablecoins
            "usdt": TokenInfo("Tether", "USDT", "tether", ["usdt", "tether"]),
            "tether": TokenInfo("Tether", "USDT", "tether", ["usdt", "tether"]),
            
            "usdc": TokenInfo("USD Coin", "USDC", "usd-coin", ["usdc", "usd coin"]),
            
            "dai": TokenInfo("Dai", "DAI", "dai", ["dai"]),
            
            # DeFi tokens
            "uniswap": TokenInfo("Uniswap", "UNI", "uniswap", ["uni", "uniswap"]),
            "uni": TokenInfo("Uniswap", "UNI", "uniswap", ["uni", "uniswap"]),
            
            "aave": TokenInfo("Aave", "AAVE", "aave", ["aave"]),
            
            "compound": TokenInfo("Compound", "COMP", "compound-governance-token", ["comp", "compound"]),
            "comp": TokenInfo("Compound", "COMP", "compound-governance-token", ["comp", "compound"]),
            
            # Layer 2 & Scaling
            "arbitrum": TokenInfo("Arbitrum", "ARB", "arbitrum", ["arb", "arbitrum"]),
            "arb": TokenInfo("Arbitrum", "ARB", "arbitrum", ["arb", "arbitrum"]),
            
            "optimism": TokenInfo("Optimism", "OP", "optimism", ["op", "optimism"]),
            "op": TokenInfo("Optimism", "OP", "optimism", ["op", "optimism"]),
        }
    
    def _initialize_query_patterns(self) -> List[str]:
        """Initialize query patterns for better token extraction"""
        return [
            r"about\s+(\w+)",
            r"tell.*about\s+(\w+)",
            r"what.*is\s+(\w+)",
            r"price.*of\s+(\w+)",
            r"analysis.*of\s+(\w+)",
            r"(\w+)\s+price",
            r"(\w+)\s+analysis",
            r"(\w+)\s+news",
            r"buy\s+(\w+)",
            r"sell\s+(\w+)",
            r"(\w+)(?:\s+cryptocurrency|\s+crypto|\s+coin|\s+token)?$"
        ]
    
    def extract_token_info(self, query: str) -> Optional[Dict[str, str]]:
        """Extract token information from user query"""
        if not query:
            return None
        
        query = query.lower().strip()
        
        # Direct mapping check
        token_info = self._check_direct_mapping(query)
        if token_info:
            return self._token_info_to_dict(token_info)
        
        # Pattern-based extraction
        token_info = self._extract_using_patterns(query)
        if token_info:
            return self._token_info_to_dict(token_info)
        
        # Fallback: try to find any known token in the query
        token_info = self._fallback_extraction(query)
        if token_info:
            return self._token_info_to_dict(token_info)
        
        return None
    
    def _check_direct_mapping(self, query: str) -> Optional[TokenInfo]:
        """Check for direct token mapping"""
        # Remove common words
        cleaned_query = self._clean_query(query)
        
        for token_key, token_info in self.token_mapping.items():
            if token_key == cleaned_query:
                return token_info
            
            # Check aliases
            if token_info.aliases:
                for alias in token_info.aliases:
                    if alias.lower() == cleaned_query:
                        return token_info
        
        return None
    
    def _extract_using_patterns(self, query: str) -> Optional[TokenInfo]:
        """Extract token using regex patterns"""
        for pattern in self.query_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                token_candidate = match.group(1).lower()
                if token_candidate in self.token_mapping:
                    return self.token_mapping[token_candidate]
        
        return None
    
    def _fallback_extraction(self, query: str) -> Optional[TokenInfo]:
        """Fallback extraction method"""
        words = query.split()
        
        # Check each word against token mapping
        for word in words:
            cleaned_word = word.lower().strip(".,!?;:")
            if cleaned_word in self.token_mapping:
                return self.token_mapping[cleaned_word]
        
        # Check for partial matches
        for word in words:
            cleaned_word = word.lower().strip(".,!?;:")
            for token_key, token_info in self.token_mapping.items():
                if cleaned_word in token_key or token_key in cleaned_word:
                    return token_info
        
        return None
    
    def _clean_query(self, query: str) -> str:
        """Clean query by removing common words and punctuation"""
        common_words = {
            "about", "tell", "me", "what", "is", "the", "price", "of", 
            "analysis", "news", "latest", "current", "today", "now",
            "cryptocurrency", "crypto", "coin", "token", "currency"
        }
        
        # Remove punctuation and split
        cleaned = re.sub(r'[^\w\s]', '', query)
        words = cleaned.split()
        
        # Filter out common words
        filtered_words = [word for word in words if word.lower() not in common_words]
        
        return " ".join(filtered_words).strip()
    
    def _token_info_to_dict(self, token_info: TokenInfo) -> Dict[str, str]:
        """Convert TokenInfo to dictionary"""
        return {
            "name": token_info.name,
            "symbol": token_info.symbol,
            "id": token_info.id
        }
    
    def add_custom_token(self, name: str, symbol: str, coingecko_id: str, aliases: List[str] = None):
        """Add custom token to mapping"""
        token_info = TokenInfo(name, symbol, coingecko_id, aliases or [])
        self.token_mapping[name.lower()] = token_info
        self.token_mapping[symbol.lower()] = token_info
        
        if aliases:
            for alias in aliases:
                self.token_mapping[alias.lower()] = token_info
    
    def get_supported_tokens(self) -> List[str]:
        """Get list of supported token names"""
        unique_tokens = set()
        for token_info in self.token_mapping.values():
            unique_tokens.add(f"{token_info.name} ({token_info.symbol})")
        return sorted(list(unique_tokens))
    
    def suggest_similar_tokens(self, query: str) -> List[str]:
        """Suggest similar tokens based on partial matching"""
        query = query.lower()
        suggestions = []
        
        for token_key, token_info in self.token_mapping.items():
            if query in token_key or token_key in query:
                suggestion = f"{token_info.name} ({token_info.symbol})"
                if suggestion not in suggestions:
                    suggestions.append(suggestion)
        
        return suggestions[:5]  # Return top 5 suggestions