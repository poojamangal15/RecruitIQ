import streamlit as st
from pypdf import PdfReader
import pandas as pd

from chains import Chain
from utils import (
    clean_text,
    extract_job_skills,
    extract_structured_info,
    load_job_description,
    map_skills,
    compute_skill_match_score,
)


def create_streamlit_app(llm: Chain, clean_text_fn):
    st.title("📄 Cover Letter and Interview Q&A Generator")

    resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    job_input = st.text_area("Job Description or URL")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Cover Letter"):
            if not resume_file or not job_input:
                st.error("Please provide both a resume and a job description or URL.")
            else:
                try:
                    pdf_reader = PdfReader(resume_file)
                    resume_text = "".join(
                        page.extract_text() or "" for page in pdf_reader.pages
                    )
                    resume_text = clean_text_fn(resume_text)
                    resume_info = extract_structured_info(resume_text)
                    job_description = load_job_description(job_input)

                    job_skills = extract_job_skills(job_description)
                    skill_map = map_skills(resume_info["skills"], job_skills)
                    score, breakdown = compute_skill_match_score(
                        resume_text, job_skills
                    )
                    concise_letter = llm.write_cover_letter(
                        resume_info, job_description, style="concise"
                    )
                    detailed_letter = llm.write_cover_letter(
                        resume_info, job_description, style="detailed"
                    )

                    st.session_state.update(
                        {
                            "concise_text": concise_letter,
                            "detailed_text": detailed_letter,
                            "skill_map": skill_map,
                            "score": score,
                            "breakdown": breakdown,
                            "cover_letter_generated": True,
                        }
                    )
                except Exception as e:
                    st.error(f"An Error Occurred: {e}")

    with col2:
        if st.button("Generate Interview Q&A"):
            if not resume_file or not job_input:
                st.error("Please provide both a resume and a job description or URL.")
            else:
                try:
                    pdf_reader = PdfReader(resume_file)
                    resume_text = "".join(
                        page.extract_text() or "" for page in pdf_reader.pages
                    )
                    resume_text = clean_text_fn(resume_text)
                    resume_info = extract_structured_info(resume_text)
                    job_description = load_job_description(job_input)
                    qa_pairs = llm.generate_interview_qa(resume_info, job_description)
                    st.session_state.update(
                        {"qa_pairs": qa_pairs, "qa_generated": True}
                    )
                except Exception as e:
                    st.error(f"An Error Occurred: {e}")

    if st.session_state.get("cover_letter_generated"):
        st.subheader("Cover Letter Versions")
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Concise")
            st.text_area("Concise Cover Letter", key="concise_text", height=300)
        with col_b:
            st.subheader("Detailed")
            st.text_area("Detailed Cover Letter", key="detailed_text", height=300)

        st.subheader("Refine Cover Letter")
        st.selectbox(
            "Version to refine", ["Concise", "Detailed"], key="version_select"
        )
        st.selectbox(
            "Tone", ["Default", "Formal", "Friendly", "Confident"], key="tone_select"
        )
        st.text_input(
            "Additional instructions (optional)", key="refine_instruction"
        )


        def apply_refinement():
            version_to_refine = st.session_state.version_select
            tone = st.session_state.tone_select
            instructions = st.session_state.refine_instruction
            refine_instructions = (
                f"Rewrite in a {tone.lower()} tone. " if tone != "Default" else ""
            )
            refine_instructions += instructions
            target_key = (
                "concise_text" if version_to_refine == "Concise" else "detailed_text"
            )
            if refine_instructions.strip():
                st.session_state[target_key] = llm.refine_cover_letter(
                    st.session_state[target_key], refine_instructions
                )

        st.button("Apply Refinement", on_click=apply_refinement)

        final_choice = st.radio(
            "Select final version", ["Concise", "Detailed"], key="final_choice"
        )

        def finalize_cover_letter():
            choice = st.session_state.final_choice
            st.session_state["final_letter"] = (
                st.session_state.concise_text
                if choice == "Concise"
                else st.session_state.detailed_text
            )

        st.button("Finalize Cover Letter", on_click=finalize_cover_letter)
        if st.session_state.get("final_letter"):
            st.subheader("Final Cover Letter")
            st.code(st.session_state.final_letter, language="markdown")

        st.subheader("Skill Match Analysis")
        st.metric("Overall Score", f"{st.session_state.score * 100:.1f}%")
        if st.session_state.breakdown:
            chart_df = pd.DataFrame(
                {
                    "Skill": list(st.session_state.breakdown.keys()),
                    "Relevance": [
                        v * 100 for v in st.session_state.breakdown.values()
                    ],
                }
            ).set_index("Skill")
            st.bar_chart(chart_df)

        if st.session_state.skill_map["matched"]:
            st.info(
                "Matched skills: " + ", ".join(st.session_state.skill_map["matched"])
            )
        if st.session_state.skill_map["gaps"]:
            st.warning(
                "Skill gaps: " + ", ".join(st.session_state.skill_map["gaps"])
            )

    if st.session_state.get("qa_generated"):
        st.subheader("Interview Q&A")
        st.code(st.session_state.qa_pairs, language="markdown")


if __name__ == "__main__":
    chain = Chain()
    st.set_page_config(
        layout="wide",
        page_title="Cover Letter and Interview Q&A Generator",
        page_icon="📄",

    )
    create_streamlit_app(chain, clean_text)

