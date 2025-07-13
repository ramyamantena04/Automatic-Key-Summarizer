
import streamlit as st
from transformers import pipeline
import requests
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO

st.set_page_config(page_title="Automatic Key Summarizer", layout="wide")

# Load summarizer once
@st.cache_resource
def load_summarizer():
    return pipeline("summarization")

summarizer = load_summarizer()

# Text chunking
def chunk_text(text, max_chunk_length=1000):
    sentences = text.split('. ')
    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(chunk) + len(sentence) <= max_chunk_length:
            chunk += sentence + ". "
        else:
            chunks.append(chunk.strip())
            chunk = sentence + ". "
    if chunk:
        chunks.append(chunk.strip())
    return chunks

# Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

# Extract text from URL
def extract_text_from_url(url):
    try:
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, "html.parser")
        paragraphs = soup.find_all("p")
        return " ".join(p.get_text() for p in paragraphs)
    except Exception as e:
        return f"Error loading URL: {e}"

# App UI
st.title("📝 Automatic Key Summarizer")

input_type = st.radio("Choose Input Type", ["Text", "URL", "PDF File"])

user_input = ""
if input_type == "Text":
    user_input = st.text_area("Paste your paragraph here", height=250)
elif input_type == "URL":
    url = st.text_input("Enter article URL")
    if url:
        st.info("Extracting text from URL...")
        user_input = extract_text_from_url(url)
        st.text_area("Extracted Text", value=user_input, height=250)
elif input_type == "PDF File":
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    if uploaded_file:
        user_input = extract_text_from_pdf(uploaded_file)
        st.text_area("Extracted Text", value=user_input, height=250)

# Summarize and display key points
if st.button("Summarize"):
    if not user_input.strip():
        st.warning("Please enter or upload some content to summarize.")
    else:
        with st.spinner("Summarizing..."):
            chunks = chunk_text(user_input)
            key_points = []

            for chunk in chunks:
                summary = summarizer(chunk, max_length=150, min_length=40, do_sample=False)
                points = summary[0]['summary_text'].split('. ')
                for pt in points:
                    if pt.strip():
                        key_points.append(f"- {pt.strip()}.")

            if key_points:
                st.subheader("📝 Key Points")
                for point in key_points:
                    st.write(point)
            else:
                st.error("No key points found.")
