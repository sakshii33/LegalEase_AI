import streamlit as st

st.set_page_config(page_title="LegalEase AI", layout="wide")

# 🚫 Hide sidebar navigation
st.markdown(
    """
    <style>
        .st-emotion-cache-1avcm0n {display: none;}
        .st-emotion-cache-6qob1r {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# 🎯 Landing Page
st.title("📄 LegalEase AI")
st.write("Welcome! Please login to access your dashboard and profile.")

# 👉 Button to go to Login Page
if st.button("🔑 Go to Login"):
    st.switch_page("pages/login.py")
