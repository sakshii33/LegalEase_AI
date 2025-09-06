from textblob import TextBlob
from transformers import pipeline
import textstat
import docx2txt
import PyPDF2

# -------------------
# Grammar correction
# -------------------
def correct_text(user_input: str) -> str:
    return str(TextBlob(user_input).correct())

# -------------------
# Load HuggingFace model
# -------------------
def load_model():
    return pipeline("text2text-generation", model="google/flan-t5-base")

simplifier_model = load_model()

def simplify_text(text: str) -> str:
    result = simplifier_model(
        f"Simplify this text: {text}",
        max_length=512,
        truncation=True
    )
    return result[0]['generated_text']

# -------------------
# Readability scores
# -------------------
def readability_score(text: str) -> dict:
    return {
        "Flesch Ease": textstat.flesch_reading_ease(text),
        "Grade Level": textstat.flesch_kincaid_grade(text),
        "Gunning Fog": textstat.gunning_fog(text)
    }

# -------------------
# File text extraction
# -------------------
def extract_text(uploaded_file):
    """Extract plain text from txt, pdf, or docx uploads"""
    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8", errors="ignore")

    elif uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return docx2txt.process(uploaded_file)

    else:
        return None
