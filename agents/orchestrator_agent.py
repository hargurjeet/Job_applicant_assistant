import json, os
import logging
from langchain.schema import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
from tools.orchestrator_tools import parse_resume_skills, extract_jd_skills, compare_skills, suggest_resume_improvements

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create Gemini model
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL_NAME,
    google_api_key=GEMINI_API_KEY,
    temperature=0,
)

# Tool registry
TOOLS = {
    "parse_resume_skills": parse_resume_skills,
    "extract_jd_skills": extract_jd_skills,
    "compare_skills": compare_skills,
    "suggest_resume_improvements": suggest_resume_improvements
}

SYSTEM_PROMPT = """
You are an AI orchestrator that decides which tool to call based on the user request.
You have access to the following tools:

1. parse_resume_skills(resume_path: str) -> Extracts skills from a resume PDF.
2. extract_jd_skills(jd_text: str) -> Extracts skills from job description text.
3. compare_skills(skills_input: JSON) -> Compares resume and JD skills. 
   JSON format: {"resume_skills": [...], "jd_skills": [...]}
4. suggest_resume_improvements(comparison_result: dict) -> Suggests improvements to resume.

When you respond, ALWAYS return valid JSON in this format:
{
    "tool": "<tool_name>",
    "input": <tool_input>
}

You may call multiple tools step by step until you can complete the task.
After using a tool, include its result in your next decision.
Continue until you can return the final comparison.

"""

def orchestrator(user_input: str):
    """
    Multi-step autonomous loop:
      1) Ask LLM which tool to run next (always JSON).
      2) Run the tool via .invoke().
      3) Update state & feed back concise state+last result.
      4) Stop after compare_skills.
    Includes logging + guardrails to avoid infinite loops.
    """
    import re

    logger.info("=== [Orchestrator] Incoming User Input ===")
    logger.info(user_input)
    
    # ---- Helper: clean ```json ... ``` fences ----
    def _clean_json_block(text: str) -> str:
        s = text.strip()
        # Remove triple backticks with optional "json"
        if s.startswith("```"):
            s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.IGNORECASE)
            s = re.sub(r"\s*```$", "", s)
        # Some models prefix with "json\n"
        if s.lower().startswith("json"):
            s = s[4:].strip()
        return s.strip()

    # ---- Track state across steps ----
    state = {
        "resume_skills": [],   # list[str]
        "jd_skills": []        # list[str]
    }
    
     # Basic guardrails
    MAX_STEPS = 6
    last_decision = None
    same_decision_count = 0

    # System prompt stays constant
    base_system = SystemMessage(content=SYSTEM_PROMPT)

    for step in range(1, MAX_STEPS + 1):
        # Compose a compact context for the LLM each turn
        decision_prompt = f"""
                        User request:
                        {user_input}

                        CURRENT_STATE:
                        resume_skills: {state["resume_skills"]}
                        jd_skills: {state["jd_skills"]}

                        If resume_skills is empty, call parse_resume_skills with the file path provided by the user.
                        If jd_skills is empty, call extract_jd_skills with the job description (file path or raw text).
                        If both are present, call compare_skills with:
                        {{"resume_skills": {state["resume_skills"]}, "jd_skills": {state["jd_skills"]} }}

                        Respond with ONLY JSON:
                        {{"tool": "<tool_name>", "input": <tool_input>}}
                        """.strip()
    
    
        messages = [base_system, HumanMessage(content=decision_prompt)]

        decision_raw = llm.invoke(messages).content
        # print("\n=== [Orchestrator] Raw LLM Decision ===")
        # print(repr(decision_raw))

        # Parse JSON
        cleaned = _clean_json_block(decision_raw)

        try:
            decision = json.loads(cleaned)
        except Exception as e:
            print("\n[Orchestrator] Failed to parse LLM JSON. Cleaned text was:")
            print(cleaned)
            return f"Error: could not parse LLM decision JSON ({e})."

        # print("\n=== [Orchestrator] Parsed JSON Decision ===")
        # print(decision)

        tool_name = decision.get("tool")
        tool_input = decision.get("input")

        # Guard: tool must exist
        if tool_name not in TOOLS:
            return f"Error: Tool '{tool_name}' not found."

        # Guard: avoid infinite repeats on the exact same decision
        if decision == last_decision:
            same_decision_count += 1
        else:
            same_decision_count = 0
        last_decision = decision
        if same_decision_count >= 2:
            return "Stopped: model repeated the same decision 3 times. Check prompts/state."

        # Invoke tool
        tool = TOOLS[tool_name]
        try:
            result = tool.invoke(tool_input if not isinstance(tool_input, dict) else json.dumps(tool_input))
        except Exception as e:
            print("\n[Orchestrator] Tool invocation error:", str(e))
            return f"Error: tool '{tool_name}' failed with: {e}"

        # print("\n=== [Orchestrator] Tool Output ===")
        # print(result)

        # Update state after tools that extract skills
        if tool_name == "parse_resume_skills":
            # Tools return comma-separated string; normalize to sorted, lowercase unique
            if isinstance(result, str):
                skills = sorted({s.strip().lower() for s in result.split(",") if s.strip()})
                state["resume_skills"] = skills
                print("\n[State] Updated resume_skills:", skills)

        elif tool_name == "extract_jd_skills":
            if isinstance(result, str):
                skills = sorted({s.strip().lower() for s in result.split(",") if s.strip()})
                state["jd_skills"] = skills
                print("\n[State] Updated jd_skills:", skills)

        elif tool_name == "compare_skills":
            # Done. compare_skills returns a dict.
            print()
            print(result)
            
             # Automatically call advisor tool
            advisor_result = TOOLS["suggest_resume_improvements"].invoke({"comparison_result": result})
            print("\n=== [Advisor Final Suggestions] ===")
            return advisor_result
    
    return "Stopped: max steps reached without running compare_skills."
    