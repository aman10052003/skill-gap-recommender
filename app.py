import fitz
import nltk
import requests
from flask import Flask, render_template, request
from skills_data import subdomain_skills
nltk.download('punkt')

app = Flask(__name__)

class PDFParser:
    def __init__(self, file_stream):
        self.file_stream = file_stream
        self.text = self.extract_text()

    def extract_text(self):
        try:
            with fitz.open(stream=self.file_stream.read(), filetype="pdf") as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return ""

    def extract_skills(self, skill_list):
        skills_found = set()
        text_lower = self.text.lower()

        # Extract individual words and common phrases
        words = nltk.word_tokenize(text_lower)
        bigrams = [' '.join(bigram) for bigram in nltk.ngrams(words, 2)]
        trigrams = [' '.join(trigram) for trigram in nltk.ngrams(words, 3)]

        all_phrases = words + bigrams + trigrams

        # Check for skills in the text
        for skill in skill_list:
            skill_lower = skill.lower()
            if any(skill_lower in phrase for phrase in all_phrases):
                skills_found.add(skill)

        return list(skills_found)

def get_all_skills():
    """Extract all unique skills from the subdomain_skills dictionary."""
    all_skills = set()
    for domain in subdomain_skills.values():
        for subdomain in domain.values():
            all_skills.update(subdomain)
    return list(all_skills)

def get_domain_for_skill(skill):
    """Find the domain(s) a skill belongs to."""
    domains = []
    for domain_name, domain in subdomain_skills.items():
        for subdomain in domain.values():
            if skill in subdomain:
                domains.append(domain_name)
    return list(set(domains))
def get_project_recommendations(job_skills):
    """
    Fetch project recommendations based on matched subdomain skills,
    returning one project per subdomain with multiple compatible skills.
    Ensures no duplicate projects are recommended based on the same skill,
    but allows the skill to appear in the matched skills list.
    """
    # Convert job skills to lowercase for case-insensitive matching
    job_skills_lower = [skill.lower() for skill in job_skills]

    # Find all matching skills across all domains and subdomains
    domain_matches = {}
    used_skills_for_fetching = set()  # Skills that have been used for fetching projects

    for domain, specializations in subdomain_skills.items():
        domain_matches[domain] = {}
        for specialization, skills in specializations.items():
            # Get all matching skills for the specialization
            matching_skills = [skill for skill in skills if skill.lower() in job_skills_lower]
            if matching_skills:
                domain_matches[domain][specialization] = matching_skills

    # Sort domains by number of matching skills to prioritize subdomains with more matches
    sorted_domains = sorted(domain_matches.items(),
                            key=lambda x: sum(len(skills) for skills in x[1].values()),
                            reverse=True)

    # Fetch one project per subdomain with multiple compatible skills
    project_suggestions = []
    headers = {"Accept": "application/vnd.github+json"}

    for domain, specializations in sorted_domains:
        for specialization, skills in specializations.items():
            # Separate out skills already used for fetching
            new_skills_to_use = [skill for skill in skills if skill.lower() not in used_skills_for_fetching]
            if new_skills_to_use:
                # Build query from new skills to fetch the project
                skill_query = "+".join(new_skills_to_use)
                url = f"https://api.github.com/search/repositories?q={skill_query}+language:Python&sort=stars"
                try:
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        projects = response.json().get("items", [])
                        if projects:
                            # Add the project to suggestions, showing both used and unused skills for the subdomain
                            project_suggestions.append({
                                "domain": domain,
                                "specialization": specialization,
                                "name": projects[0]["full_name"],
                                "url": projects[0]["html_url"],
                                "description": projects[0]["description"],
                                "stars": projects[0]["stargazers_count"],
                                "skills_matched": skills,  # Include all matching skills for context
                            })
                            # Mark the new skills as used for fetching purposes
                            used_skills_for_fetching.update(skill.lower() for skill in new_skills_to_use)
                except requests.RequestException:
                    continue

    # If no projects found, return a default response
    return project_suggestions if project_suggestions else [{
        "domain": "No relevant projects found.",
        "specialization": "No relevant specialization found.",
        "name": "No relevant projects found.",
        "url": "",
        "description": "Try adjusting your skill set or search criteria.",
        "stars": 0,
        "skills_matched": [],
    }]


def get_coursera_courses(skill):
    url = f"https://api.coursera.org/api/courses.v1?q=search&query={skill}"
    response = requests.get(url)
    if response.status_code == 200:
        courses = response.json().get("elements", [])
        course_data = []

        # Limit to a maximum of 5 courses
        for course in courses[:3]:  # Take only the first 3 courses
            course_name = course.get("name")
            course_slug = course.get("slug")  # This may be empty or incorrect sometimes
            if course_slug:
                course_url = f"https://www.coursera.org/learn/{course_slug}"
            else:
                course_url = "#"  # Fallback URL or placeholder
            course_data.append((course_name, course_url))

        return course_data if course_data else [("No courses found", "#")]
    return [("Error fetching Coursera courses", "#")]

@app.route("/", methods=["GET", "POST"])
def index():
    results = {}
    error = None

    if request.method == "POST":
        resume_file = request.files.get("resume")
        job_description_file = request.files.get("job_description")

        if not resume_file or not job_description_file:
            error = "Please upload both resume and job description files."
        else:
            try:
                # Parse PDFs
                resume_parser = PDFParser(resume_file)
                job_parser = PDFParser(job_description_file)

                # Get all possible skills from our database
                all_skills = get_all_skills()

                # Extract skills from both documents
                resume_skills = resume_parser.extract_skills(all_skills)
                job_skills = job_parser.extract_skills(all_skills)

                # Find missing skills
                missing_skills = list(set(job_skills) - set(resume_skills))
                course_recommendations = {skill: get_coursera_courses(skill) for skill in missing_skills}
                project_recommendations = get_project_recommendations(job_skills)

                # Organize skills by domain
                resume_skills_by_domain = {}
                job_skills_by_domain = {}
                missing_skills_by_domain = {}

                for skill in resume_skills:
                    domains = get_domain_for_skill(skill)
                    for domain in domains:
                        if domain not in resume_skills_by_domain:
                            resume_skills_by_domain[domain] = []
                        resume_skills_by_domain[domain].append(skill)

                for skill in job_skills:
                    domains = get_domain_for_skill(skill)
                    for domain in domains:
                        if domain not in job_skills_by_domain:
                            job_skills_by_domain[domain] = []
                        job_skills_by_domain[domain].append(skill)

                for skill in missing_skills:
                    domains = get_domain_for_skill(skill)
                    for domain in domains:
                        if domain not in missing_skills_by_domain:
                            missing_skills_by_domain[domain] = []
                        missing_skills_by_domain[domain].append(skill)

                results = {
                    "resume_skills": resume_skills,
                    "job_skills": job_skills,
                    "missing_skills": missing_skills,
                    "resume_skills_by_domain": resume_skills_by_domain,
                    "job_skills_by_domain": job_skills_by_domain,
                    "missing_skills_by_domain": missing_skills_by_domain,
                    "course_recommendations": course_recommendations,
                    "project_suggestions": project_recommendations
                }

            except Exception as e:
                error = f"An error occurred while processing the files: {str(e)}"

    return render_template("index.html", results=results, error=error)

if __name__ == "__main__":
    app.run(debug=True)