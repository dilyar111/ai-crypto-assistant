# 🧠 AI Crypto Assistant

A simple cryptocurrency analysis tool that combines real-time market data with AI insights using local Llama models.

## ✨ What It Does

- 📊 **Real-time crypto data** - prices, market cap, volume from Binance & CoinGecko
- 📰 **Latest news** - cryptocurrency news from CryptoPanic
- 🤖 **AI analysis** - smart insights using local Llama 2/3 models
- 🌐 **Multi-language** - Russian and English support

## 🚀 Quick Start

### 1. Install Requirements

```bash
# Clone and install
git clone https://github.com/dilyar111/ai-crypto-assistant.git
cd ai-crypto-assistant
pip install -r requirements.txt

# Install Ollama and pull model
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama2
```

### 2. Setup API Key (Optional)

Create `.env` file:
```env
CRYPTOPANIC_API_KEY=your_api_key_here
```
Get free key at: https://cryptopanic.com/developers/api/

### 3. Run

```bash
streamlit run app.py
```

Open http://localhost:8501 and start asking about cryptocurrencies!

## 📱 Usage

Just type natural questions like:
- "Tell me about Bitcoin"
- "What's happening with Ethereum?"
- "Analyze Solana trends"

The app will show:
- 💰 Current price and 24h change
- 📊 Market data and rankings  
- 📰 Latest news headlines
- 🤖 AI-powered analysis

## 🛠️ Troubleshooting

**AI not working?**
```bash
# Check Ollama is running
ollama list
# If empty, pull a model
ollama pull llama2
```

**Need help?**
```bash
# Run diagnostics
python troubleshoot.py
```

## 🎯 Supported Cryptocurrencies

Bitcoin, Ethereum, Cardano, Solana, Dogecoin, Polkadot, Chainlink, Polygon, and 40+ more popular cryptocurrencies.

## 📁 Project Structure

```
ai-crypto-assistant/
├── app.py              # Main application
├── app_debug.py        # Debug version
├── troubleshoot.py     # Diagnostics tool
├── assistant/          # Core modules
├── requirements.txt    # Dependencies
└── .env               # API keys
```

## 🔧 Configuration

### AI Models
- `llama2` - Default, balanced performance
- `llama3` - More advanced reasoning
- `mistral` - Fast and efficient

### Analysis Modes
- **Basic** - Quick overview
- **Detailed** - Comprehensive analysis
- **Deep** - Technical deep-dive

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Make changes
4. Submit pull request

## 📄 License

MIT License - see LICENSE file

## ⚠️ Disclaimer

This tool is for educational purposes only. Not financial advice. Always do your own research before making investment decisions.

---

**Questions?** Open an issue on GitHub!