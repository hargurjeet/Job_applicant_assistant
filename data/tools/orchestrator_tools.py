import os
import json
from langchain.tools import tool
from tools.resume_parser import parse_resume
from tools.skill_extractor import SkillExtractor

from langchain.schema import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME

skill_extractor = SkillExtractor()

# Init Gemini LLM
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL_NAME,
    google_api_key=GEMINI_API_KEY,
    temperature=0,
)

@tool("parse_resume_skills", return_direct=False)
def parse_resume_skills(resume_path: str) -> str:
    """
    Parses a resume from a given PDF file path and returns a comma-separated list of skills.
    """
    raw_text = parse_resume(resume_path)
    # skills = skill_extractor.extract_skills(text)
    # # skills = ["Python", "ML", "AWS"]  # temporary mock
    # # === Debug logging ===
    # # print("\n=== [Resume Parser] Extracted Skills ===")
    # return ", ".join(skills)
    # Create messages for LLM
    messages = [
        SystemMessage(content=(
            "You are an expert career assistant. "
            "Given a resume description, extract ONLY the relevant technical and soft skills "
            "that are important for a Data Scientist role. "
            "Return them as a comma-separated list (no explanations)."
        )),
        HumanMessage(content=raw_text)
    ]

    # Call Gemini
    response = llm.invoke(messages).content
    
    return response


@tool("extract_jd_skills", return_direct=False)
def extract_jd_skills(jd_path: str) -> str:
    """
    Extracts relevant skills from a job description text.
    """
    with open(jd_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
            
   # Create messages for LLM
    messages = [
        SystemMessage(content=(
            "You are an expert career assistant. "
            "Given a job description, extract ONLY the relevant technical and soft skills "
            "that are important for a Data Scientist role. "
            "Return them as a comma-separated list (no explanations)."
        )),
        HumanMessage(content=raw_text)
    ]

    # Call Gemini
    response = llm.invoke(messages).content
    # === Debug logging ===
    # print("\n=== [JD Parser] Extracted Skills ===")
    # print(response)
    
    return response


@tool("compare_skills", return_direct=False)
def compare_skills(inputs: str) -> str:
    """
    Compare resume skills and job description skills.
    Pass input as: "resume_skill1, resume_skill2 | jd_skill1, jd_skill2"
    """
    try:
        data = json.loads(inputs)
        resume_skills = set(data.get("resume_skills", []))
        jd_skills = set(data.get("jd_skills", []))

        common = resume_skills & jd_skills
        missing_from_resume = jd_skills - resume_skills
        extra_in_resume = resume_skills - jd_skills

        # === Debug logging ===
        # print("\n=== [Compare Skills] Resume Skills Extracted ===")
        # print(resume_skills)
        # print("\n=== [Compare Skills] JD Skills Extracted ===")
        # print(jd_skills)
        # print("\n=== [Compare Skills] Common Skills ===")
        # print(common)
        # print("\n=== [Compare Skills] Missing from Resume ===")
        # print(missing_from_resume)
        # print("\n=== [Compare Skills] Extra in Resume ===")
        # print(extra_in_resume)

        return {
            "common": list(common),
            "missing_from_resume": list(missing_from_resume),
            "extra_in_resume": list(extra_in_resume)
        }

    except Exception as e:
        print("\n[Compare Skills] Error:", str(e))
        print("Raw inputs were:", inputs)
        return {"error": str(e)}
    
@tool("suggest_resume_improvements", return_direct=False)
def suggest_resume_improvements(comparison_result: dict) -> str:
    """
    Suggests improvements to the resume based on the comparison of resume vs JD skills.
    Input: dict from compare_skills tool, e.g.
    {
        "common": [...],
        "missing_from_resume": [...],
        "extra_in_resume": [...]
    }
    Returns: Friendly recommendation text for the candidate.
    """
    try:
        if not comparison_result or not isinstance(comparison_result, dict):
            return "[Error] Invalid comparison_result input."

        missing = comparison_result.get("missing_from_resume", [])
        common = comparison_result.get("common", [])
        extra = comparison_result.get("extra_in_resume", [])

        if not missing:
            return "Great news! Your resume already covers the key skills from the job description. ✅"

        # Construct prompt for Gemini
        messages = [
            SystemMessage(content=(
                ''' You are a career assistant helping a Data Scientist improve their resume.
                    You will be given:

                    A list of skills already matched with the job description

                    A list of missing skills from the resume

                    Your task:

                    Suggest no more than 5 missing skills that would make the resume stronger for shortlisting.

                    For each suggested skill, explain in 1–2 sentences why adding it would improve the candidate’s chances.

                    Keep your tone friendly, encouraging, and realistic.

                    Do not suggest fabricating experience. Recommend adding a skill only if the candidate has genuine exposure or can quickly learn it.'''
            )),
            HumanMessage(content=f"""
                                    Matched skills: {common}
                                    Missing from resume: {missing}
                                    Extra in resume: {extra}
                                    """)
                                        ]

        response = llm.invoke(messages).content
        print("\n=== [Advisor Tool] Suggestions ===")

        return response

    except Exception as e:
        print("\n[Advisor Tool] Error:", str(e))
        return "Something went wrong while generating suggestions."