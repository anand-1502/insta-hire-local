import streamlit as st
import json
from pathlib import Path
from src.pdf_utils import extract_text_from_pdf
from src.embeddings import EmbeddingIndex
from src.db import DB
from src.settings import settings

st.title("Candidate Upload")
st.write("Upload your resume and tell us when and where you can work.")

# Init services
db = DB()
index = EmbeddingIndex()

with st.form("candidate_form", clear_on_submit=False):
    name = st.text_input("Full name", "")
    email = st.text_input("Email", "")
    phone = st.text_input("Phone", "")

    col1, col2 = st.columns(2)
    with col1:
        city = st.text_input("City", "")
        pay_min = st.number_input("Expected pay min ($/hr)", min_value=0.0, value=15.0, step=1.0)
    with col2:
        state = st.text_input("State or region", "")
        pay_max = st.number_input("Expected pay max ($/hr)", min_value=0.0, value=25.0, step=1.0)

    st.markdown("**Availability**")
    days = st.multiselect("Days available", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    times = st.multiselect("Time windows", ["morning", "afternoon", "evening", "night"])

    pdf_file = st.file_uploader("Upload resume PDF", type=["pdf"])

    submitted = st.form_submit_button("Save Candidate")

if submitted:
    if not (name and email and pdf_file and city):
        st.error("Please fill name, email, city, and upload a PDF.")
        st.stop()

    # Save PDF
    resumes_dir = Path(settings.DATA_DIR) / "resumes"
    resumes_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = resumes_dir / f"{name.replace(' ', '_')}_{pdf_file.name}"
    with open(pdf_path, "wb") as f:
        f.write(pdf_file.read())

    # Parse PDF
    resume_text = extract_text_from_pdf(pdf_path)
    if not resume_text.strip():
        st.warning("Could not extract text from this PDF. The file might be scanned or image based.")
        # Still proceed, but embedding quality will be low

    # Create embedding and add to FAISS
    emb_id = index.add_text(resume_text)

    # Save to DB
    cand_id = db.add_candidate(
        name=name,
        email=email,
        phone=phone,
        city=city,
        state=state,
        pay_min=float(pay_min),
        pay_max=float(pay_max),
        availability=json.dumps({"days": days, "times": times}),
        resume_path=str(pdf_path),
        embedding_id=emb_id,
        resume_excerpt=resume_text[:1200]  # store a short preview to display
    )

    st.success(f"Saved {name} with candidate id {cand_id}.")
    st.info("Your resume is now searchable by employers.")
