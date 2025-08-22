# Job Applicant Assistant

An AI-powered tool that helps job seekers optimize their resumes by comparing their skills against job descriptions and providing personalized improvement suggestions.

## Features

- **Resume Parsing**: Extract skills from PDF resumes using AI
- **Job Description Analysis**: Identify required skills from job postings
- **Skill Comparison**: Compare resume skills against job requirements
- **Smart Recommendations**: Get AI-powered suggestions to improve your resume
- **Interactive Web UI**: User-friendly Streamlit interface
- **Command Line Interface**: Direct script execution for automation

## Architecture

```
Job_applicant_assistant/
├── agents/
│   └── orchestrator_agent.py    # Main AI orchestrator
├── tools/
│   └── orchestrator_tools.py    # Core processing tools
├── ui/
│   └── streamlit_app.py         # Web interface
├── data/
│   └── uploads_resumes/         # Resume storage
├── config.py                    # Configuration settings
└── main.py                      # CLI entry point
```

## Installation

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Job_applicant_assistant
   ```

2. **Install dependencies**
   ```bash
   pip install langchain langchain-google-genai streamlit PyPDF2
   ```

3. **Set up environment variables**
   ```bash
   export GEMINI_API_KEY="your-gemini-api-key"
   ```
   
   Or create a `.env` file:
   ```
   GEMINI_API_KEY=your-gemini-api-key
   ```

## Usage

### Web Interface (Recommended)

1. **Start the Streamlit app**
   ```bash
   streamlit run ui/streamlit_app.py
   ```

2. **Upload and analyze**
   - Upload your resume (PDF format)
   - Paste the job description
   - Click "Extract & Compare Skills"
   - Get improvement suggestions

### Command Line Interface

```bash
python main.py
```

*Note: Update file paths in `main.py` to match your resume and job description locations.*

## How It Works

1. **Resume Parsing**: AI extracts technical and soft skills from your PDF resume
2. **Job Analysis**: AI identifies required skills from the job description
3. **Skill Matching**: Compares your skills against job requirements
4. **Gap Analysis**: Identifies missing skills and extra qualifications
5. **Recommendations**: Provides actionable suggestions to improve your resume

## Configuration

Edit `config.py` to customize:

```python
# AI Model Configuration
GEMINI_MODEL_NAME = "gemini-2.5-flash"  # Model version
GEMINI_API_KEY = "your-api-key"         # Your API key
```

## Example Output

```
Common Skills:
- Python, Machine Learning, AWS, SQL

Missing Skills:
- Docker, Kubernetes, Apache Spark

Extra Skills:
- React, Node.js, MongoDB

Suggestions:
1. Add Docker experience - containerization is crucial for ML deployment
2. Highlight Apache Spark skills - big data processing is highly valued
3. Consider mentioning Kubernetes - shows cloud-native expertise
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

**API Key Error**
```
Error: GEMINI_API_KEY not found
```
*Solution: Set your Gemini API key in environment variables or config.py*

**PDF Parsing Error**
```
Error: Could not parse PDF
```
*Solution: Ensure PDF is not password-protected and contains readable text*

**Module Import Error**
```
ModuleNotFoundError: No module named 'langchain'
```
*Solution: Install required dependencies using pip*

## Future Enhancements

- [ ] Support for multiple resume formats (DOCX, TXT)
- [ ] Batch processing for multiple job applications
- [ ] Resume template suggestions
- [ ] ATS (Applicant Tracking System) optimization
- [ ] Industry-specific skill recommendations
- [ ] Integration with job boards

---

**Made for job seekers everywhere**