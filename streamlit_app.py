import streamlit as st
import requests
import json
from streamlit_extras.stylable_container import stylable_container

# API Configuration
API_URL = "http://127.0.0.1:8000"  # Change if hosted elsewhere

# Custom CSS for styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #ffffff;
    }
    .password-display {
        font-family: 'Courier New', monospace;
        font-size: 24px;
        letter-spacing: 2px;
        background: #2a2a3a;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 20px 0;
        border: 1px solid #444;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6e48aa 0%, #9d50bb 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 25px;
        font-weight: bold;
    }
    .stSelectbox, .stTextInput, .stSlider {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 8px;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.title("🔐 AI Password Generator")
st.markdown("Generate secure, memorable passwords using AI")

# Sidebar for API Configuration
with st.sidebar:
    st.header("Settings")
    api_url = st.text_input("API URL", API_URL)
    st.markdown("---")
    st.markdown("**Password Types:**")
    st.markdown("- `word`: Dictionary words (e.g., alphabravo)")
    st.markdown("- `cap`: Capital letters (e.g., ABCD)")
    st.markdown("- `num`: Numbers (e.g., 1234)")
    st.markdown("- `special`: Symbols (e.g., @!#$)")

# Main Content
col1, col2 = st.columns(2)

with col1:
    ptype = st.selectbox(
        "Password Type",
        ["word", "cap", "num", "special"],
        index=0,
        help="Choose the type of password to generate"
    )

    seed = st.text_input(
        "Starting Characters",
        value="ab" if ptype == "word" else "AB" if ptype == "cap" else "12" if ptype == "num" else "@!",
        help="Provide 2-3 starting characters"
    )

with col2:
    length = st.slider(
        "Password Length",
        min_value=6,
        max_value=20,
        value=12,
        step=1
    )

    temperature = st.slider(
        "Creativity Level",
        min_value=0.1,
        max_value=2.0,
        value=0.8,
        step=0.1,
        help="Lower = more predictable, Higher = more random"
    )

# Generate Button
if st.button("✨ Generate Password", use_container_width=True):
    try:
        response = requests.get(
            f"{api_url}/generate-password",
            params={
                "ptype": ptype,
                "seed": seed,
                "length": length,
                "temperature": temperature
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Display password with copy button
            with stylable_container(
                key="password_container",
                css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
                }
                """,
            ):
                st.markdown(f"### Your Generated Password")
                st.markdown(f'<div class="password-display">{result["password"]}</div>', unsafe_allow_html=True)
                
                # Copy functionality
                st.code(result["password"], language="text")
                if st.button("📋 Copy to Clipboard", key="copy_button"):
                    st.session_state.copied = True
                    st.experimental_show("Password copied!")
                    
            # Password details
            st.success(f"Generated {result['type']} password with length {result['length']}")
            
        else:
            st.error(f"API Error: {response.json().get('error', 'Unknown error')}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")