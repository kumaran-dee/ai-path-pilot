import json
import urllib.request

# NOTE: No Gemini calls in this file! The /dashboard/scan endpoint must complete
# in under 5 seconds to avoid Vercel's 10-second serverless timeout.

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
        """
        Fast, pure-Python keyword algorithm.
        No AI calls to avoid Vercel 10-second serverless timeout.
        """
        bio = (bio or "").lower()
        skills_lower = [s.lower() for s in (skills or [])]
        skills_display = [s for s in (skills or [])]

        detected_skills = set(skills_display)

        # Map keywords found in bio to display skill names
        keywords = {
            "python": "Python",
            "java": "Java",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "machine learning": "Machine Learning",
            "deep learning": "Deep Learning",
            "data science": "Data Science",
            "sql": "SQL",
            "react": "React",
            "node": "Node.js",
            "django": "Django",
            "flask": "Flask",
            "docker": "Docker",
            "aws": "AWS",
            "kubernetes": "Kubernetes",
            "git": "Git",
            "mongodb": "MongoDB",
            "postgresql": "PostgreSQL",
            "linux": "Linux",
            "tensorflow": "TensorFlow",
            "pytorch": "PyTorch",
        }

        # Detect skills from bio text
        full_text = bio + " " + " ".join(skills_lower)
        for key, value in keywords.items():
            if key in full_text:
                detected_skills.add(value)

        # Build recommendations based on detected skills
        jobs = []
        internships = []
        workshops = []
        hackathons = []
        leetcode = []
        missing_skills = []

        detected_lower = {s.lower() for s in detected_skills}

        if "python" in detected_lower:
            jobs.extend(["Python Developer", "Backend Developer", "AI Engineer"])
            internships.extend(["Python Backend Intern", "Data Engineering Intern"])
            leetcode.extend(["Two Sum", "Valid Parentheses", "Binary Search", "Merge Intervals"])

        if "machine learning" in detected_lower or "tensorflow" in detected_lower or "pytorch" in detected_lower:
            jobs.extend(["ML Engineer", "Data Scientist", "AI Research Engineer"])
            internships.extend(["Machine Learning Intern", "Data Science Intern"])
            workshops.extend(["MLOps Workshop", "Deep Learning Bootcamp"])
            hackathons.extend(["AI Hackathon", "Data Science Challenge"])
            leetcode.extend(["Kth Largest Element", "Top K Frequent Elements", "Number of Islands"])

        if "react" in detected_lower or "javascript" in detected_lower or "typescript" in detected_lower:
            jobs.extend(["Frontend Developer", "React Developer", "Full Stack Developer"])
            internships.extend(["Frontend Dev Intern", "React Intern"])
            workshops.extend(["Advanced React Patterns", "Next.js Bootcamp"])
            hackathons.extend(["Build With AI Hackathon", "Global Hack Week"])
            leetcode.extend(["Valid Parentheses", "LRU Cache", "Design Hit Counter"])

        if "sql" in detected_lower or "postgresql" in detected_lower or "mongodb" in detected_lower:
            jobs.extend(["Database Engineer", "Backend Developer"])
            leetcode.extend(["Department Top Three Salaries", "Rank Scores"])

        if "java" in detected_lower:
            jobs.extend(["Java Developer", "Spring Boot Engineer"])
            internships.extend(["Java Backend Intern"])
            leetcode.extend(["Word Search", "Course Schedule"])

        # Detect missing critical skills
        critical_skills = ["Docker", "AWS", "Git", "SQL", "Linux"]
        for skill in critical_skills:
            if skill.lower() not in detected_lower:
                missing_skills.append(skill)

        # Calculate career score based on breadth of skills
        career_score = min(100, len(detected_skills) * 8)

        # Fallback defaults when no skills detected at all
        if not jobs:
            jobs = ["Software Engineer", "Full Stack Developer", "Junior Developer"]
            internships = ["Software Engineering Intern", "Web Dev Intern"]
            workshops = ["System Design Basics", "Clean Code Principles"]
            hackathons = ["Smart India Hackathon", "Global Hack Week"]
            leetcode = ["Two Sum", "Merge Intervals", "LRU Cache"]

        return {
            "career_score": career_score,
            "detected_skills": sorted(list(detected_skills)),
            "missing_skills": missing_skills,
            "jobs": list(dict.fromkeys(jobs))[:5],           # unique, preserve order
            "internships": list(dict.fromkeys(internships))[:4],
            "workshops": list(dict.fromkeys(workshops))[:4],
            "hackathons": list(dict.fromkeys(hackathons))[:4],
            "leetcode_problems": list(dict.fromkeys(leetcode))[:5]
        }

    def _is_valid_link(self, platform: str, value: str) -> bool:
        if platform == "resume":
            return value.lower().endswith(".pdf")
            
        # Allow just usernames for github/leetcode
        if platform in ["github", "leetcode"] and " " not in value and not value.startswith("http"):
            return True
            
        if not value.startswith("http://") and not value.startswith("https://"):
            return False
            
        # Trust the frontend validation — no HTTP pings to avoid Vercel timeout
        return True

    def _scan_github(self, url_or_username: str) -> dict:
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
                score = min(100, 40 + (public_repos * 2) + (followers * 5))
                return {"username": name, "score": score}
        except Exception as e:
            print(f"GitHub API Error: {e}")
            return self._simulate_scan("github", url_or_username)
            
    def _simulate_scan(self, platform: str, value: str) -> dict:
        """Fast, instant profile score — no AI calls."""
        username = "Profile Found"
        if "linkedin.com/in/" in value:
            # Strip UTM params and clean up the username from the URL
            path = value.split("linkedin.com/in/")[-1].split("?")[0].strip("/")
            username = path.replace("-", " ").title()
        elif "github.com/" in value:
            username = value.split("github.com/")[-1].strip("/")
        elif "leetcode.com/u/" in value or "leetcode.com/" in value:
            username = value.split("leetcode.com/")[-1].strip("/").replace("u/", "")

        return {"username": username or "Profile Found", "score": 85}

    def _parse_json(self, text: str, default: dict) -> dict:
        try:
            if text.startswith("```json"):
                text = text[7:-3]
            elif text.startswith("```"):
                text = text[3:-3]
            text = text.strip()
            return json.loads(text)
        except Exception:
            return default

profile_scanner = ProfileScanner()
