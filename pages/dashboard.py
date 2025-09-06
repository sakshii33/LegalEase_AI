import streamlit as st
from database import SessionLocal, Document
from backend.simplifier import correct_text, simplify_text, readability_score, extract_text

st.set_page_config(page_title="Dashboard", layout="wide")

# 🚫 Hide sidebar nav
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebarCollapsedControl"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ Check login
if "user" not in st.session_state:
    st.warning("⚠️ Please login first.")
    st.switch_page("Login.py")
    st.stop()

user = st.session_state["user"]

# ---------------- Sidebar Navigation ----------------
with st.sidebar:
    st.title("📍 Navigation")
    nav_choice = st.radio("Go to:", ["Dashboard", "Profile", "Logout"])

if nav_choice == "Profile":
    st.switch_page("pages/Profile.py")
elif nav_choice == "Logout":
    st.session_state.clear()
    st.success("✅ Logged out successfully. Redirecting...")
    st.switch_page("pages/Login.py")

# ---------------- Dashboard Content ----------------
st.title("🤖 LegalEase AI")

# Initialize chat + results in session
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "👋 Hi! Upload a document or ask me anything."}]

if "last_doc" not in st.session_state:
    st.session_state.last_doc = None  # store latest doc results here

# 1️⃣ Load from DB if session empty
if st.session_state.last_doc is None:
    db = SessionLocal()
    latest_doc = db.query(Document).filter_by(user_id=user.id).order_by(Document.upload_date.desc()).first()
    db.close()
    if latest_doc:
        st.session_state.last_doc = {
            "title": latest_doc.title,
            "content": latest_doc.content,
            "simplified": latest_doc.simplified_content,
            "scores_before": {
                "Flesch Ease": latest_doc.flesch_ease_before,
                "Grade Level": latest_doc.grade_before,
                "Gunning Fog": latest_doc.fog_before,
            },
            "scores_after": {
                "Flesch Ease": latest_doc.flesch_ease_after,
                "Grade Level": latest_doc.grade_after,
                "Gunning Fog": latest_doc.fog_after,
            }
        }

# 2️⃣ Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 3️⃣ Chat input
if user_input := st.chat_input("Type your message here..."):
    corrected = correct_text(user_input)

    st.session_state.messages.append({"role": "user", "content": corrected})
    with st.chat_message("user"):
        st.write(corrected)

    if "upload" in corrected.lower() or "document" in corrected.lower():
        response = "📄 Sure! Please upload your document below."
        st.session_state.upload_mode = True
    else:
        response = "I can simplify contracts and policies. Please upload a document to begin."

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)

# 4️⃣ File uploader inside chat
if "upload_mode" not in st.session_state:
    st.session_state.upload_mode = False

if st.session_state.upload_mode:
    uploaded_file = st.file_uploader("Upload a contract/policy document", type=["pdf", "docx", "txt"])
    if uploaded_file:
        text = extract_text(uploaded_file)
        if text:
            simplified = simplify_text(text)
            scores_before = readability_score(text)
            scores_after = readability_score(simplified)

            # ✅ Save latest doc in session
            st.session_state.last_doc = {
                "title": uploaded_file.name,
                "content": text,
                "simplified": simplified,
                "scores_before": scores_before,
                "scores_after": scores_after
            }

            # ✅ Save to DB
            db = SessionLocal()
            doc = Document(
                title=uploaded_file.name,
                content=text,
                simplified_content=simplified,
                flesch_ease_before=scores_before["Flesch Ease"],
                flesch_ease_after=scores_after["Flesch Ease"],
                grade_before=scores_before["Grade Level"],
                grade_after=scores_after["Grade Level"],
                fog_before=scores_before["Gunning Fog"],
                fog_after=scores_after["Gunning Fog"],
                user_id=user.id
            )
            db.add(doc)
            db.commit()
            db.close()

            st.rerun()

# 5️⃣ Show last document results
if st.session_state.last_doc:
    doc = st.session_state.last_doc
    with st.chat_message("assistant"):
        st.success(f"✅ Last simplified document: {doc['title']}")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📄 Original Text")
            st.write(doc["content"][:1000] + "...")  # excerpt
        with col2:
            st.subheader("✨ Simplified Text")
            st.write(doc["simplified"])

        # Show readability scores
        st.markdown("### 📊 Readability Scores")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Before Simplification**")
            st.metric("Flesch Ease", doc["scores_before"]["Flesch Ease"])
            st.metric("Grade Level", doc["scores_before"]["Grade Level"])
            st.metric("Gunning Fog", doc["scores_before"]["Gunning Fog"])
        with c2:
            st.markdown("**After Simplification**")
            st.metric("Flesch Ease", doc["scores_after"]["Flesch Ease"])
            st.metric("Grade Level", doc["scores_after"]["Grade Level"])
            st.metric("Gunning Fog", doc["scores_after"]["Gunning Fog"])
