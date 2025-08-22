import streamlit as st
import tempfile
import json

from tools.orchestrator_tools import parse_resume_skills, extract_jd_skills, compare_skills, suggest_resume_improvements

st.set_page_config(page_title="Resume vs JD Skill Matcher", layout="wide")

st.title("📊 Resume vs Job Description Skill Matcher")

resume_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
jd_text = st.text_area("📝 Paste Job Description")

if st.button("Extract & Compare Skills"):
    if not resume_file:
        st.error("Please upload a resume PDF first.")
        st.stop()
    if not jd_text.strip():
        st.error("Please paste a job description first.")
        st.stop()

    # Save resume to a temp path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(resume_file.read())
        resume_path = tmp_pdf.name

    # Save JD text to a temp path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp_jd:
        tmp_jd.write(jd_text)
        jd_path = tmp_jd.name

    st.info("✅ Files saved. Extracting skills...")

    # === Step 1: Extract Skills ===
    resume_skills = parse_resume_skills.invoke(resume_path)
    jd_skills = extract_jd_skills.invoke(jd_path)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Resume Skills")
        st.write(resume_skills)

    with col2:
        st.subheader("📝 JD Skills")
        st.write(jd_skills)
    
    # Ensure resume_skills and jd_skills are lists
    if isinstance(resume_skills, str):
        resume_skills = [s.strip() for s in resume_skills.split(",") if s.strip()]

    if isinstance(jd_skills, str):
        jd_skills = [s.strip() for s in jd_skills.split(",") if s.strip()]
    
    st.write("🔎 Resume skills list:", resume_skills)
    st.write("🔎 JD skills list:", jd_skills)

    # === Step 2: Compare Skills ===
    comparison = compare_skills.invoke(json.dumps({"resume_skills": resume_skills,"jd_skills": jd_skills}))

    st.subheader("🔍 Skill Comparison")

    st.markdown("**✅ Common Skills:**")
    st.write(comparison.get("common", []))

    st.markdown("**❌ Missing Skills (Not in Resume):**")
    st.write(comparison.get("missing_from_resume", []))

    st.markdown("**🎯 Extra Skills (Only in Resume):**")
    st.write(comparison.get("extra_in_resume", []))
    
    st.session_state["resume_skills"] = resume_skills
    st.session_state["jd_skills"] = jd_skills
    st.session_state["comparison"] = comparison

# === Step 3: Generate Resume Improvement Suggestions ===
if st.button("Suggest Resume Improvements"):
    resume_skills = st.session_state.get("resume_skills", [])
    jd_skills = st.session_state.get("jd_skills", [])
    comparison = st.session_state.get("comparison", {})
    
    try:
        improvements = suggest_resume_improvements.invoke({
                                                            "resume_skills": resume_skills,
                                                            "jd_skills": jd_skills,
                                                            "comparison_result": comparison
                                                        })

        st.subheader("✨ Suggested Improvements")
        if isinstance(improvements, dict) and "error" in improvements:
            st.error(improvements["error"])
        else:
            # Improvements may come as string or list
            if isinstance(improvements, str):
                st.write(improvements)
            elif isinstance(improvements, list):
                for idx, suggestion in enumerate(improvements, 1):
                    st.markdown(f"**{idx}.** {suggestion}")
            else:
                st.json(improvements)

    except Exception as e:
        st.error(f"Error generating improvements: {e}")
