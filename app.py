import streamlit as st

st.set_page_config(page_title="InstaHire Local", page_icon="🍽️", layout="wide")

st.title("InstaHire Local 🍽️")
st.write("A simple, local tool to match restaurant jobs with the best resumes.")

st.markdown("""
### How it works
- Candidates upload a PDF resume and provide location, availability, and expected pay.
- The app parses the PDF, creates an embedding, and stores everything locally.
- Employers enter a job description and basic filters to find the top matches.

Use the sidebar to switch between pages.
""")
