from agents.orchestrator_agent import orchestrator
    
if __name__ == "__main__":
    # Let Gemini decide the flow and call tools
    result = orchestrator(
        "Parse the resume from /home/ec2-user/SageMaker/notebooks/hargurjeet/Isolated_developments/langchain_pro/job_application_assistant/data/Hargurjeet_Resume_v1.pdf, "
        "extract the skills from this job description in /home/ec2-user/SageMaker/notebooks/hargurjeet/Isolated_developments/langchain_pro/job_application_assistant/data/sample_jd.txt, "
        "and compare them."
    )

    print("\n=== Final Output ===")
    print(result)