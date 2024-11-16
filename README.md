#skill-gap-recommender
SkillSync: Your AI Career Assistant 
SkillSync is a web-based application designed to enhance resumes and boost career prospects by analyzing resume and job descriptions. It identifies missing skills, recommends courses, and suggests projects to help users align their resumes with job requirements effectively.

Features
Upload Functionality: Upload resume and job description PDFs directly through the interface.
Skill Analysis: Extracts skills from resumes and job descriptions to highlight missing skills.
Course Recommendations: Suggests relevant online courses (from platforms like Udemy, Coursera, etc.) to bridge skill gaps.
Project Suggestions: Recommends GitHub projects based on skills and job requirements, including information about stars and domains.
Real-Time Feedback: Interactive UI to display results dynamically, with animations for better user experience.
Tech Stack

Frontend:
HTML5, CSS3, JavaScript
SVG Icons for visuals
Backend:
Python (Flask)
Machine Learning for skill extraction and project/course recommendation
Libraries & APIs:
PyPDF2, spaCy, GitHub API, and external course recommendation APIs
Deployment:
Streamlit for analysis results display
Docker for containerization (optional)
Installation
Prerequisites
Python 3.8+
Flask
pipenv or pip for package management
Steps to Set Up

Install dependencies:
bash
pip install -r requirements.txt  
Run the application:
bash
python app.py  
Access the application at http://127.0.0.1:5000/.

Usage
Navigate to the homepage.

Upload your resume and job description in PDF format.
Click Analyze Documents.

View the analyzed results, including:

Resume skills

Required job skills

Missing skills

Course and project recommendations

Folder Structure
 
├── app.py              # Flask backend script  
├── templates/          # HTML templates for frontend  
│   ├── index.html      # Main interface  
├── requirements.txt    # Python dependencies 
├──skills_data          #all cs/it related skills divided in different domains and subdomains       
├── README.md           # Project documentation  


Future Scope
Integrate more APIs for course recommendations.
Add support for multiple file formats like Word documents.
Enable multi-language resume parsing using advanced NLP models.
Enhance skill matching with more industry domains beyond CS/IT.
Acknowledgements
OpenAI for guidance.
GitHub API for project recommendations.
Online course platforms for course suggestions.
