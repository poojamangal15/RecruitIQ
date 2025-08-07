import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-8b-8192")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are Mohan, a business development executive at AtliQ. AtliQ is an AI & Software Consulting company dedicated to facilitating
            the seamless integration of business processes through automated tools. 
            Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
            process optimization, cost reduction, and heightened overall efficiency. 
            Your job is to write a cold email to the client regarding the job mentioned above describing the capability of AtliQ 
            in fulfilling their needs.
            Also add the most relevant ones from the following links to showcase Atliq's portfolio: {link_list}
            Remember you are Mohan, BDE at AtliQ. 
            Do not provide a preamble.
            ### EMAIL (NO PREAMBLE):

            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return res.content

    def write_cover_letter(
        self, resume_info: Dict[str, List[str]], job_description: str, style: str = "standard"
    ) -> str:
        resume_summary = (
            f"Skills: {', '.join(resume_info.get('skills', []))}\n"
            f"Education: {'; '.join(resume_info.get('education', []))}\n"
            f"Experience: {'; '.join(resume_info.get('experience', []))}"
        )
        prompt_cover = PromptTemplate.from_template(
            """
            ### RESUME INFORMATION:
            {resume_summary}

            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            Using the resume information and job description above, write a {style} professional cover letter highlighting the most relevant experience and skills that match the job requirements.

            Tailor the letter to the position and avoid any preamble or closing unrelated to the letter itself.
            ### COVER LETTER:
            """
        )
        chain_cover = prompt_cover | self.llm
        res = chain_cover.invoke(
            {
                "resume_summary": resume_summary,
                "job_description": job_description,
                "style": style,
            }
        )

        return res.content

    def refine_cover_letter(self, cover_letter: str, instructions: str) -> str:
        """Refine a cover letter based on user-provided instructions."""
        prompt_refine = PromptTemplate.from_template(
            """
            ### CURRENT COVER LETTER:
            {cover_letter}

            ### INSTRUCTION:
            {instructions}

            Rewrite the cover letter accordingly while preserving key information.
            ### REVISED COVER LETTER:
            """
        )
        chain_refine = prompt_refine | self.llm
        res = chain_refine.invoke(
            {"cover_letter": cover_letter, "instructions": instructions}
        )
        return res.content

    def generate_interview_qa(
        self, resume_info: Dict[str, List[str]], job_description: str, num_questions: int = 5
    ) -> str:
        """Generate interview questions and answers based on the resume and job description."""
        resume_summary = (
            f"Skills: {', '.join(resume_info.get('skills', []))}\n"
            f"Education: {'; '.join(resume_info.get('education', []))}\n"
            f"Experience: {'; '.join(resume_info.get('experience', []))}"
        )

        prompt_qa = PromptTemplate.from_template(
            """
            ### RESUME INFORMATION:
            {resume_summary}

            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            Generate {num_questions} potential interview questions for this role. For each question, craft a concise answer using details from the resume information above.
            Format the result as numbered list in Markdown:

            1. **Question:** ...\n   **Answer:** ...

            Do not include any preamble or text outside the list.
            ### INTERVIEW Q&A:
            """
        )
        chain_qa = prompt_qa | self.llm
        res = chain_qa.invoke(
            {
                "resume_summary": resume_summary,
                "job_description": job_description,
                "num_questions": num_questions,
            }
        )

        return res.content

    def generate_interview_qa(
        self, resume_info: Dict[str, List[str]], job_description: str, num_questions: int = 5
    ) -> str:
        """Generate interview questions and answers based on the resume and job description."""
        resume_summary = (
            f"Skills: {', '.join(resume_info.get('skills', []))}\n"
            f"Education: {'; '.join(resume_info.get('education', []))}\n"
            f"Experience: {'; '.join(resume_info.get('experience', []))}"
        )

        prompt_qa = PromptTemplate.from_template(
            """
            ### RESUME INFORMATION:
            {resume_summary}

            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            Generate {num_questions} potential interview questions for this role. For each question, craft a concise answer using details from the resume information above.
            Format the result as numbered list in Markdown:

            1. **Question:** ...\n   **Answer:** ...

            Do not include any preamble or text outside the list.
            ### INTERVIEW Q&A:
            """
        )
        chain_qa = prompt_qa | self.llm
        res = chain_qa.invoke(
            {
                "resume_summary": resume_summary,
                "job_description": job_description,
                "num_questions": num_questions,
            }
        )

        return res.content

if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))
