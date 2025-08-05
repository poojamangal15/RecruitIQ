import streamlit as st
from pypdf import PdfReader

from chains import Chain
from utils import clean_text


def create_streamlit_app(llm: Chain, clean_text_fn):
    st.title("📄 Cover Letter Generator")

    resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    job_description = st.text_area("Job Description")

    if st.button("Generate Cover Letter"):
        if not resume_file or not job_description:
            st.error("Please provide both a resume and a job description.")
            return

        try:
            pdf_reader = PdfReader(resume_file)
            resume_text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
            resume_text = clean_text_fn(resume_text)
            cover_letter = llm.write_cover_letter(resume_text, job_description)
            st.code(cover_letter, language="markdown")
        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    st.set_page_config(layout="wide", page_title="Cover Letter Generator", page_icon="📄")
    create_streamlit_app(chain, clean_text)

