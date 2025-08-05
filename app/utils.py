import re
from typing import Dict, List
from urllib.parse import urlparse

import requests
import spacy
from bs4 import BeautifulSoup

from spacy.matcher import PhraseMatcher


def clean_text(text: str) -> str:
    """Basic cleanup for extracted text."""
    # Remove HTML tags
    text = re.sub(r"<[^>]*?>", "", text)

    # Remove URLs
    text = re.sub(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "",
        text,
    )

    # Remove special characters
    text = re.sub(r"[^a-zA-Z0-9 ]", "", text)

    # Replace multiple spaces with a single space
    text = re.sub(r"\s{2,}", " ", text)

    # Trim leading and trailing whitespace
    text = text.strip()

    # Remove extra whitespace
    text = " ".join(text.split())

    return text


def load_job_description(job_input: str) -> str:
    """Return job description text, fetching it if ``job_input`` is a URL."""
    parsed = urlparse(job_input.strip())
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        resp = requests.get(job_input)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator=" ")
        return clean_text(text)
    return job_input

_SKILLS = [
    "python",
    "java",
    "c++",
    "javascript",
    "sql",
    "machine learning",
    "data analysis",
    "project management",
    "communication",
    "leadership",
]


nlp = spacy.load("en_core_web_sm")
_skill_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
_skill_matcher.add("SKILLS", [nlp.make_doc(skill) for skill in _SKILLS])


def extract_structured_info(text: str) -> Dict[str, List[str]]:
    """Extract skills, education, and experience from resume text."""
    doc = nlp(text)
    skills = {doc[start:end].text for _, start, end in _skill_matcher(doc)}

    education, experience = [], []
    for sent in doc.sents:
        sentence = sent.text.strip()
        if re.search(r"\b(Bachelor|Master|B\.Sc|M\.Sc|PhD|University|College)\b", sentence, re.I):
            education.append(sentence)
        if re.search(r"\b\d+\+? years? of experience\b", sentence, re.I):
            experience.append(sentence)

    return {
        "skills": sorted(skills),
        "education": education,
        "experience": experience,
    }


def extract_job_skills(text: str) -> List[str]:
    """Extract skills mentioned in a job description."""
    doc = nlp(text)
    skills = {doc[start:end].text for _, start, end in _skill_matcher(doc)}
    return sorted(skills)


def map_skills(resume_skills: List[str], job_skills: List[str]) -> Dict[str, List[str]]:
    """Map resume skills to job requirements and highlight gaps."""
    resume_set = {s.lower() for s in resume_skills}
    job_set = {s.lower() for s in job_skills}
    matched = sorted(job_set & resume_set)
    gaps = sorted(job_set - resume_set)
    return {"matched": matched, "gaps": gaps}
