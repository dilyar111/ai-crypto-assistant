import time
import streamlit as st
from assistant.query_handler import extract_token_name
from assistant.data_fetcher import get_news, get_price, get_market_data
from assistant.response_generator import generate_response

st.set_page_config(page_title="🧠 AI Crypto Assistant")
st.title("🧠 AI Crypto Assistant")

query = st.text_input("Ask about a cryptocurrency (e.g., 'Tell me about Ethereum')")

if query:
    with st.spinner("Analyzing query..."):
        token = extract_token_name(query)
        st.write(f"🔍 Token extracted: {token}")

        try:
            start = time.time()
            st.write("⏳ Fetching news...")
            news = get_news(token)
            st.write(f"✅ News fetched in {time.time() - start:.2f}s")

            start = time.time()
            st.write("⏳ Fetching price...")
            price = get_price(token.upper())
            st.write(f"✅ Price fetched in {time.time() - start:.2f}s")

            start = time.time()
            st.write("⏳ Fetching market data...")
            market_data = get_market_data(token.lower())
            st.write(f"✅ Market data fetched in {time.time() - start:.2f}s")

            start = time.time()
            st.write("⏳ Generating response from Ollama...")
            prompt = (
                f"News:\n{news}\n\n"
                f"Price:\n{price}\n\n"
                f"Market data:\n{market_data}\n\n"
                f"Token: {token}\n\n"
                "Расскажи об этой криптовалюте."
            )
            response = generate_response(prompt)
            st.write(f"✅ Response generated in {time.time() - start:.2f}s")

            st.success(response)

        except Exception as e:
            st.error(f"❌ Error fetching data: {e}")

def main():
    prompt = "Что ты знаешь о биткоине?"
    answer = generate_response(prompt)
    print("Ответ модели:", answer)

if __name__ == "__main__":
    main()
