import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
    SBERT_AVAILABLE = True
except:
    SBERT_AVAILABLE = False


class SkillJobRecommender:

    def __init__(self):

        self.jobs = [
            {
                "title": "Data Scientist",
                "skills": [
                    "python", "machine learning", "pandas",
                    "numpy", "sql", "statistics"
                ],
                "description": "Analyze data and build machine learning models",
                "experience": "mid"
            },
            {
                "title": "Python Developer",
                "skills": [
                    "python", "sql", "flask",
                    "django", "git", "api"
                ],
                "description": "Develop applications using Python",
                "experience": "entry"
            },
            {
                "title": "Data Analyst",
                "skills": [
                    "python", "sql", "excel",
                    "pandas", "power bi", "statistics"
                ],
                "description": "Analyze data and create reports",
                "experience": "entry"
            },
            {
                "title": "Full Stack Developer",
                "skills": [
                    "html", "css", "javascript",
                    "python", "sql", "git"
                ],
                "description": "Develop frontend and backend web applications",
                "experience": "mid"
            },
            {
                "title": "Machine Learning Engineer",
                "skills": [
                    "python", "machine learning",
                    "tensorflow", "numpy", "pandas"
                ],
                "description": "Build and deploy machine learning models",
                "experience": "senior"
            }
        ]

        self.job_text = [
            " ".join(job["skills"])
            for job in self.jobs
        ]

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english"
        )

        self.job_matrix = self.vectorizer.fit_transform(
            self.job_text
        )

        self.model = None

        if SBERT_AVAILABLE:

            try:
                self.model = SentenceTransformer(
                    "all-MiniLM-L6-v2"
                )

                self.job_embeddings = self.model.encode(
                    self.job_text
                )

            except:

                self.model = None
                self.job_embeddings = None

        else:

            self.job_embeddings = None


    def recommend_jobs(self, user_skills, experience="entry"):

        user_text = " ".join(user_skills)

        if self.model is not None:

            user_embedding = self.model.encode(
                [user_text]
            )

            similarity = cosine_similarity(
                user_embedding,
                self.job_embeddings
            ).flatten()

        else:

            user_vector = self.vectorizer.transform(
                [user_text]
            )

            similarity = cosine_similarity(
                user_vector,
                self.job_matrix
            ).flatten()

        indices = np.argsort(
            similarity
        )[::-1]

        recommendations = []

        for index in indices[:5]:

            job = self.jobs[index]

            score = similarity[index] * 100

            if job["experience"] == experience:
                score = score * 1.10

            score = min(
                95,
                max(15, int(score))
            )

            recommendations.append({
                "title": job["title"],
                "skills": job["skills"],
                "description": job["description"],
                "experience": job["experience"],
                "match_score": score
            })

        return recommendations


recommender = SkillJobRecommender()


def recommend_job_roles(
    skills,
    experience="entry"
):

    return recommender.recommend_jobs(
        skills,
        experience
    )


def get_skill_gap(user_skills, job):

    user_skills = [
        skill.lower().strip()
        for skill in user_skills
    ]

    required_skills = [
        skill.lower()
        for skill in job["skills"]
    ]

    missing_skills = []

    for skill in required_skills:

        if skill not in user_skills:
            missing_skills.append(skill)

    return missing_skills


def get_learning_path(missing_skills):

    learning = {
        "python": "Learn Python",
        "sql": "Learn SQL",
        "machine learning": "Learn Machine Learning",
        "tensorflow": "Learn TensorFlow",
        "numpy": "Learn NumPy",
        "pandas": "Learn Pandas",
        "statistics": "Learn Statistics",
        "flask": "Learn Flask",
        "django": "Learn Django",
        "git": "Learn Git",
        "html": "Learn HTML",
        "css": "Learn CSS",
        "javascript": "Learn JavaScript"
    }

    path = []

    for skill in missing_skills:

        if skill in learning:
            path.append(
                learning[skill]
            )
        else:
            path.append(
                "Learn " + skill.title()
            )

    return path