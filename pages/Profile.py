import os
import streamlit as st
from backend.auth import Session, User, Document

UPLOAD_DIR = "uploads/profile_pics"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="Profile", layout="wide")

# 🚫 Hide Streamlit’s default sidebar nav + hamburger
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebarCollapsedControl"] {display: none;}

        /* Card style */
        .card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .profile-pic {
            display: block;
            margin-left: auto;
            margin-right: auto;
            border-radius: 50%;
            border: 3px solid #ddd;
        }

        .section-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .doc-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 15px;
            border: 1px solid #eee;
            border-radius: 8px;
            margin-bottom: 8px;
        }

        .doc-actions {
            display: flex;
            gap: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ Ensure login
if "user" not in st.session_state:
    st.warning("⚠️ Please login first.")
    st.switch_page("Login.py")
    st.stop()

# ---------------- Sidebar Navigation ----------------
with st.sidebar:
    st.title("📍 Navigation")
    nav_choice = st.radio("Go to:", ["Profile", "Dashboard", "Logout"])

if nav_choice == "Dashboard":
    st.switch_page("pages/Dashboard.py")
elif nav_choice == "Logout":
    st.session_state.clear()
    st.success("✅ Logged out successfully. Redirecting...")
    st.switch_page("pages/Login.py")

# ---------------- Profile Content ----------------
user = st.session_state["user"]
session = Session()
db_user = session.query(User).filter_by(id=user.id).first()

# Layout: Two columns
col1, col2 = st.columns([1, 2])

# LEFT COLUMN: Profile Image
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Profile Image</div>', unsafe_allow_html=True)

    if db_user.profile_image and os.path.exists(db_user.profile_image):
        st.image(db_user.profile_image, width=128, output_format="PNG")
    else:
        st.image("https://via.placeholder.com/128", width=128)

    uploaded_img = st.file_uploader("Choose Image", type=["png", "jpg", "jpeg"])
    if uploaded_img:
        img_path = os.path.join(UPLOAD_DIR, f"user_{db_user.id}.png")
        with open(img_path, "wb") as f:
            f.write(uploaded_img.getbuffer())
        db_user.profile_image = img_path
        session.commit()
        st.success("✅ Profile image updated.")
        st.rerun()

    if st.button("Remove Image"):
        if db_user.profile_image and os.path.exists(db_user.profile_image):
            os.remove(db_user.profile_image)
        db_user.profile_image = None
        session.commit()
        st.success("🗑️ Profile image removed.")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT COLUMN: Personal Details
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Personal Details</div>', unsafe_allow_html=True)

    new_name = st.text_input("Name", value=db_user.username)
    new_email = st.text_input("Email", value=db_user.email, disabled=True)
    new_phone = st.text_input("Phone", value=db_user.phone or "")

    if st.button("Update Profile"):
        db_user.username = new_name
        db_user.phone = new_phone
        session.commit()
        st.success("✅ Profile updated.")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# DOCUMENTS Section
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📄 Documents</div>', unsafe_allow_html=True)

docs = session.query(Document).filter_by(user_id=db_user.id).all()

if docs:
    for doc in docs:
        st.markdown(
            f"""
            <div class="doc-row">
                <div><b>{doc.title}</b> <br><small>Uploaded at: {doc.upload_date.strftime('%Y-%m-%d %H:%M')}</small></div>
                <div class="doc-actions">
            """,
            unsafe_allow_html=True
        )

        colA, colB = st.columns([1, 1])

        with colA:
            new_name = st.text_input(f"Rename {doc.id}", value=doc.title, key=f"rename_{doc.id}")
            if st.button(f"Save Rename {doc.id}"):
                if new_name.strip() and new_name != doc.title:
                    doc.title = new_name.strip()
                    session.commit()
                    st.success("✅ Renamed successfully.")
                    st.rerun()

        with colB:
            if st.button(f"Delete {doc.id}"):
                session.delete(doc)
                session.commit()
                st.success("🗑️ Deleted successfully.")
                st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)
else:
    st.info("No documents uploaded yet.")

st.markdown('</div>', unsafe_allow_html=True)

session.close()
