# RecruitIQ

RecruitIQ is a Streamlit application that helps candidates craft tailored cover letters and prepare for interviews.

## Features
- **Cover Letter Generator**: Upload a resume (PDF) and provide a job description to create concise and detailed cover letter drafts.
- **Interactive Editing**: Adjust tone, refine content with custom instructions, and compare concise and detailed versions side by side before finalizing.
- **Interview Q&A Generator**: Produce potential interview questions with suggested answers based on the resume and job description.
- **Skill Match Analysis**: Visualize how your skills align with the job requirements and identify gaps.

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the `GROQ_API_KEY` environment variable.
3. Run the Streamlit app:
   ```bash
   streamlit run app/main.py
   ```

## Testing
Run the test suite with:
```bash
pytest
```

