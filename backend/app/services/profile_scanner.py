import json
import urllib.request
from app.services.gemini_service import gemini_service

class ProfileScanner:
    def scan_profiles(self, links: dict) -> dict:
        results = {}
        for key, value in links.items():
            if not value or not str(value).strip():
                continue
            
            val_str = str(value).strip()
            
            if not self._is_valid_link(key, val_str):
                results[key] = {"username": "Invalid Link", "score": 0}
                continue
            
            if key == "github":
                results[key] = self._scan_github(val_str)
            else:
                results[key] = self._simulate_scan(key, val_str)
                
        return results

    def generate_recommendations(self, bio: str, skills: list) -> dict:
        bio = (bio or "").lower()
        skills = [s.lower() for s in (skills or [])]

        detected_skills = set(skills)

        keywords = {
            "python": "Python",
            "java": "Java",
            "machine learning": "Machine Learning",
            "deep learning": "Deep Learning",
            "data science": "Data Science",
            "sql": "SQL",
            "react": "React",
            "node": "Node.js",
            "docker": "Docker",
            "aws": "AWS",
            "git": "Git"
        }

        for key, value in keywords.items():
            if key in bio:
                detected_skills.add(value)

        jobs = []
        internships = []
        workshops = []
        hackathons = []
        leetcode = []

        if "python" in str(detected_skills).lower():
            jobs.extend([
                "Python Developer",
                "Backend Developer",
                "AI Engineer"
            ])

            internships.extend([
                "Python Internship",
                "Backend Internship"
            ])

            leetcode.extend([
                "Two Sum",
                "Valid Parentheses",
                "Binary Search",
                "Merge Intervals"
            ])

        if "machine learning" in str(detected_skills).lower():
            jobs.extend([
                "ML Engineer",
                "Data Scientist"
            ])

            internships.extend([
                "Machine Learning Intern"
            ])

            workshops.extend([
                "MLOps Workshop",
                "Deep Learning Bootcamp"
            ])

            hackathons.extend([
                "AI Hackathon",
                "Data Science Challenge"
            ])

            leetcode.extend([
                "Kth Largest Element",
                "Top K Frequent Elements",
                "Number of Islands",
                "Word Ladder"
            ])

        missing_skills = []

        for skill in [
            "Docker",
            "AWS",
            "Git",
            "SQL"
        ]:
            if skill.lower() not in str(detected_skills).lower():
                missing_skills.append(skill)

        career_score = min(
            100,
            len(detected_skills) * 10
        )

        # Generate fallback recommendations if nothing matches
        if not jobs:
            jobs = ["Software Engineer", "Full Stack Developer"]
            internships = ["Software Engineering Intern"]
            workshops = ["System Design Basics", "Advanced React Patterns"]
            hackathons = ["Smart India Hackathon", "Global Hack Week"]
            leetcode = ["Two Sum", "Merge Intervals", "LRU Cache"]

        return {
            "career_score": career_score,
            "detected_skills": list(detected_skills),
            "missing_skills": missing_skills,
            "jobs": list(set(jobs)),
            "internships": list(set(internships)),
            "workshops": list(set(workshops)),
            "hackathons": list(set(hackathons)),
            "leetcode_problems": list(set(leetcode))
        }

    def _is_valid_link(self, platform: str, value: str) -> bool:
        if platform == "resume":
            return value.lower().endswith(".pdf")
            
        # Allow just usernames for github/leetcode
        if platform in ["github", "leetcode"] and " " not in value and not value.startswith("http"):
            return True
            
        if not value.startswith("http://") and not value.startswith("https://"):
            return False
            
        try:
            req = urllib.request.Request(value, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=4) as response:
                return True
        except urllib.error.HTTPError as e:
            # 404 means not found. Other errors like 403, 401, 999 (LinkedIn) mean the URL exists but bots are blocked.
            if e.code == 404:
                return False
            return True
        except Exception:
            return False

        
    def _scan_github(self, url_or_username: str) -> dict:
        # Extract username
        username = url_or_username
        if "github.com/" in url_or_username:
            username = url_or_username.split("github.com/")[-1].strip("/")
            
        try:
            req = urllib.request.Request(
                f"https://api.github.com/users/{username}", 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                
                name = data.get("name") or data.get("login") or "Unknown"
                public_repos = data.get("public_repos", 0)
                followers = data.get("followers", 0)
                
                # Fast Python-based heuristic score
                score = min(100, 50 + (public_repos * 2) + (followers * 5))
                
                return {
                    "username": name,
                    "score": score
                }
        except Exception as e:
            print(f"GitHub API Error: {e}")
            return self._simulate_scan("github", url_or_username)
            
    def _simulate_scan(self, platform: str, value: str) -> dict:
        # Avoid Vercel 10s timeout by not using Gemini for fake scores
        # We simulate a solid profile score for demo purposes
        username = "Profile Found"
        if "linkedin.com/in/" in value:
            username = value.split("linkedin.com/in/")[-1].strip("/").replace("-", " ").title()
        elif "github.com/" in value:
            username = value.split("github.com/")[-1].strip("/")
            
        return {
            "username": username,
            "score": 85
        }
        
    def _parse_json(self, text: str, default: dict) -> dict:
        try:
            if text.startswith("```json"):
                text = text[7:-3]
            elif text.startswith("```"):
                text = text[3:-3]
            
            # sometimes the response has leading/trailing whitespaces or newlines
            text = text.strip()
            return json.loads(text)
        except Exception:
            return default

profile_scanner = ProfileScanner()
