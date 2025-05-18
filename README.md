# 🧠 AI Crypto Assistant

AI Crypto Assistant is a smart Streamlit app that allows the user to ask questions about cryptocurrencies and get meaningful answers based on:

- 🔎 Latest news (via [CryptoPanic API](https://cryptopanic.com/developers/api/))
- 💸 Current price (via [Binance API](https://binance-docs.github.io/apidocs/spot/en/#ticker-price))
- 📊 Market data (via [CoinGecko API](https://www.coingecko.com/en/api))
- 🧠 Answer generation using the local [Ollama](https://ollama.com/) language model with the `llama2` model.

---

## 📦 Usage

Clone the repository:
```bash
git clone https://github.com/dilyar111/ai-crypto-assistant.git
cd ai-crypto-assistant
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Install and run Ollama:
Download: https://ollama.com/download
Command:
```bash
ollama run llama2
```
Run:
```bash
ollama serve # Run local LLM server
streamlit run app.py # Run Streamlit application
```
