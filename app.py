import time
import streamlit as st
import logging
from typing import Optional, Dict, Any
from assistant.query_handler import QueryHandler
from assistant.data_fetcher import DataFetcher
from assistant.response_generator import ResponseGenerator
from assistant.config import Config
from assistant.utils import format_currency, format_percentage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🧠 AI Crypto Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def initialize_components():
    """Initialize and cache application components"""
    config = Config()
    query_handler = QueryHandler()
    data_fetcher = DataFetcher(config)
    response_generator = ResponseGenerator(config)
    return query_handler, data_fetcher, response_generator

def display_market_data(market_data: Dict[str, Any], price_data: Dict[str, Any]):
    """Display market data in a structured format"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Current Price", 
            f"${format_currency(price_data.get('price', 0))}"
        )
    
    with col2:
        st.metric(
            "Market Cap", 
            f"${format_currency(market_data.get('market_cap', 0))}"
        )
    
    with col3:
        st.metric(
            "Market Rank", 
            f"#{market_data.get('rank', 'N/A')}"
        )
    
    with col4:
        change_24h = market_data.get('price_change_24h', 0)
        st.metric(
            "24h Change",
            f"{format_percentage(change_24h)}%",
            delta=f"{change_24h:.2f}%"
        )

def display_news(news_data: list):
    """Display news in an organized format"""
    if not news_data or not any(news_data):
        st.warning("No recent news available")
        return
    
    st.subheader("📰 Latest News")
    for i, article in enumerate(news_data[:5]):  # Show top 5 articles
        with st.expander(f"Article {i+1}: {article.get('title', 'No title')[:100]}..."):
            st.write(f"**Published:** {article.get('published_at', 'Unknown')}")
            st.write(f"**Title:** {article.get('title', 'No title')}")
            if article.get('url'):
                st.write(f"**Link:** [Read more]({article['url']})")

def main():
    st.title("🧠 AI Crypto Assistant")
    st.markdown("Get comprehensive cryptocurrency analysis powered by AI")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Language selection
        language = st.selectbox(
            "Response Language",
            ["Russian", "English"],
            index=0
        )
        
        # Model selection
        model_options = ["llama2", "llama3", "mistral", "codellama"]
        selected_model = st.selectbox(
            "AI Model",
            model_options,
            index=0
        )
        
        # Analysis depth
        analysis_depth = st.selectbox(
            "Analysis Depth",
            ["Basic", "Detailed", "Comprehensive"],
            index=1
        )
        
        st.markdown("---")
        st.markdown("**Supported cryptocurrencies:**")
        st.markdown("• Bitcoin (BTC)")
        st.markdown("• Ethereum (ETH)")
        st.markdown("• And many more...")
    
    # Initialize components
    try:
        query_handler, data_fetcher, response_generator = initialize_components()
    except Exception as e:
        st.error(f"Failed to initialize components: {e}")
        return
    
    # Main input
    query = st.text_input(
        "Ask about a cryptocurrency",
        placeholder="e.g., 'Tell me about Ethereum' or 'What's the latest on Bitcoin?'",
        help="Enter the name of any cryptocurrency you want to analyze"
    )
    
    # Analysis button
    analyze_button = st.button("🔍 Analyze", type="primary")
    
    if query and analyze_button:
        # Create progress container
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Parse query
                status_text.text("🔍 Analyzing your query...")
                progress_bar.progress(10)
                
                token_info = query_handler.extract_token_info(query)
                if not token_info:
                    st.error("❌ Could not identify cryptocurrency from your query. Please try again.")
                    return
                
                st.success(f"✅ Identified: {token_info['name']} ({token_info['symbol']})")
                progress_bar.progress(20)
                
                # Create data containers
                data_container = st.container()
                
                with data_container:
                    # Create tabs for different data types
                    tab1, tab2, tab3 = st.tabs(["📊 Market Data", "📰 News", "🤖 AI Analysis"])
                    
                    # Step 2: Fetch data concurrently
                    status_text.text("📊 Fetching market data...")
                    progress_bar.progress(40)
                    
                    # Get market data
                    market_data = data_fetcher.get_market_data(token_info['id'])
                    price_data = data_fetcher.get_price(token_info['symbol'])
                    
                    with tab1:
                        display_market_data(market_data, price_data)
                    
                    progress_bar.progress(60)
                    status_text.text("📰 Fetching latest news...")
                    
                    # Get news
                    news_data = data_fetcher.get_news(token_info['name'])
                    
                    with tab2:
                        display_news(news_data)
                    
                    progress_bar.progress(80)
                    status_text.text("🤖 Generating AI analysis...")
                    
                    # Step 3: Generate AI response
                    analysis_prompt = response_generator.create_analysis_prompt(
                        token_info=token_info,
                        market_data=market_data,
                        price_data=price_data,
                        news_data=news_data,
                        language=language.lower(),
                        depth=analysis_depth.lower()
                    )
                    
                    ai_response = response_generator.generate_response(
                        analysis_prompt, 
                        model=selected_model
                    )
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    
                    with tab3:
                        st.markdown("### 🤖 AI Analysis")
                        st.markdown(ai_response)
                        
                        # Download option
                        st.download_button(
                            label="📥 Download Analysis",
                            data=ai_response,
                            file_name=f"{token_info['name']}_analysis_{int(time.time())}.txt",
                            mime="text/plain"
                        )
                
                # Clear progress indicators
                time.sleep(1)
                progress_container.empty()
                
            except Exception as e:
                logger.error(f"Error during analysis: {e}")
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("💡 Try refreshing the page or checking your internet connection")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using Streamlit and Llama 2 | "
        "[Source Code](https://github.com/your-repo) | "
        "⚠️ This is not financial advice"
    )

if __name__ == "__main__":
    main()