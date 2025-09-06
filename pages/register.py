import streamlit as st
from backend.auth import register_user, verify_otp

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

st.title("📝 Register")

if "registered_email" not in st.session_state:
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        success, msg = register_user(username, email, password)
        st.info(msg)
        if success:
            st.session_state["registered_email"] = email  # ✅ Save email for OTP step
            st.rerun()  # 🔄 Refresh page to show OTP input
else:
    st.subheader("🔐 Verify OTP")
    otp = st.text_input("Enter OTP")
    if st.button("Verify"):
        success, msg = verify_otp(st.session_state["registered_email"], otp)
        st.info(msg)
        if success:
            del st.session_state["registered_email"]
            st.success("🎉 Account verified successfully! Redirecting to Login...")
            st.switch_page("pages/login.py")
