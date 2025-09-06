import streamlit as st
from backend.auth import login_user

st.set_page_config(page_title="Login", layout="centered")

st.title("🔑 Login")

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

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = login_user(email, password)
    if user:
        if not user.is_verified:   # ✅ FIXED
            st.warning("⚠️ Please verify your email before logging in.")
        else:
            st.session_state["user"] = user
            st.success("✅ Login successful! Redirecting to Dashboard...")
            st.switch_page("pages/Dashboard.py")
    else:
        st.error("❌ Invalid email or password")

# 🔗 Registration link
st.markdown(
    """
    <p style="margin-top:20px;">
        Don't have an account? <a href="/register" target="_self">Register here</a>
    </p>
    """,
    unsafe_allow_html=True
)
