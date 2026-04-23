"""
Dataset generation utilities for the recommendation system.

Creates synthetic data:
  - 200 students with randomized skills and interests
  - 75 courses across 10 categories
  - ~3000 ratings with realistic distributions

The rating generation is NOT purely random — students rate courses higher
when the course skills overlap with their own skills/interests, creating
a learnable signal for the recommendation models.
"""

import random
import json
import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ALL_SKILLS = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
    "SQL", "HTML/CSS", "React", "Angular", "Vue.js", "Node.js", "Django",
    "Flask", "Spring Boot", "Express.js", "Machine Learning", "Data Science",
    "Deep Learning", "NLP", "Computer Vision", "Statistics", "Linear Algebra",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git", "Linux",
    "REST APIs", "GraphQL", "Data Structures", "Algorithms",
    "Database Design", "System Design", "Agile", "DevOps", "CI/CD",
    "Cybersecurity", "Networking", "Cloud Computing", "Microservices",
    "Data Visualization", "Pandas", "NumPy", "TensorFlow", "PyTorch",
]

ALL_INTERESTS = [
    "Web Development", "Mobile Development", "AI/ML",
    "Data Engineering", "Cloud Computing", "DevOps",
    "Cybersecurity", "Game Development", "Blockchain",
    "IoT", "Robotics", "Data Visualization",
    "Backend Development", "Frontend Development", "Full Stack",
    "Open Source", "Competitive Programming", "Research",
]

CATEGORIES = [
    "Web Development", "Data Science", "Machine Learning",
    "Cloud Computing", "DevOps", "Mobile Development",
    "Cybersecurity", "Database", "Programming Fundamentals",
    "Software Engineering",
]

DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"]


def generate_courses():
    """
    Generate 75 realistic courses across different categories.
    
    Returns:
        List of dicts with keys: name, category, difficulty, description, skills_covered
    """
    courses = [
        # ── Programming Fundamentals (8) ──────────────────────────────
        {"name": "Python for Beginners", "category": "Programming Fundamentals", "difficulty": "Beginner",
         "description": "Learn Python from scratch with hands-on coding exercises and projects.", "skills_covered": ["Python"]},
        {"name": "Advanced Python Programming", "category": "Programming Fundamentals", "difficulty": "Advanced",
         "description": "Master decorators, generators, metaclasses, and concurrency in Python.", "skills_covered": ["Python", "Data Structures", "Algorithms"]},
        {"name": "Java Masterclass", "category": "Programming Fundamentals", "difficulty": "Intermediate",
         "description": "Comprehensive Java course covering OOP, collections, and multithreading.", "skills_covered": ["Java", "Data Structures"]},
        {"name": "C++ From Zero to Hero", "category": "Programming Fundamentals", "difficulty": "Intermediate",
         "description": "Deep dive into C++ including STL, templates, and memory management.", "skills_covered": ["C++", "Algorithms", "Data Structures"]},
        {"name": "Data Structures & Algorithms", "category": "Programming Fundamentals", "difficulty": "Intermediate",
         "description": "Master essential DSA concepts with implementations in Python.", "skills_covered": ["Python", "Data Structures", "Algorithms"]},
        {"name": "Go Programming Language", "category": "Programming Fundamentals", "difficulty": "Intermediate",
         "description": "Learn Go for building fast, concurrent, and reliable software.", "skills_covered": ["Go", "Microservices"]},
        {"name": "Rust Systems Programming", "category": "Programming Fundamentals", "difficulty": "Advanced",
         "description": "Memory-safe systems programming with Rust.", "skills_covered": ["Rust", "System Design"]},
        {"name": "TypeScript Deep Dive", "category": "Programming Fundamentals", "difficulty": "Intermediate",
         "description": "Advanced TypeScript patterns for scalable application development.", "skills_covered": ["TypeScript", "JavaScript"]},

        # ── Web Development (10) ─────────────────────────────────────
        {"name": "Modern React Development", "category": "Web Development", "difficulty": "Intermediate",
         "description": "Build dynamic UIs with React hooks, context, and modern patterns.", "skills_covered": ["React", "JavaScript", "HTML/CSS"]},
        {"name": "Full Stack with MERN", "category": "Web Development", "difficulty": "Advanced",
         "description": "Build complete applications with MongoDB, Express, React, and Node.js.", "skills_covered": ["React", "Node.js", "Express.js", "JavaScript", "REST APIs"]},
        {"name": "Vue.js 3 Essentials", "category": "Web Development", "difficulty": "Beginner",
         "description": "Get started with Vue.js 3 Composition API and reactive programming.", "skills_covered": ["Vue.js", "JavaScript", "HTML/CSS"]},
        {"name": "Angular Enterprise Apps", "category": "Web Development", "difficulty": "Advanced",
         "description": "Build enterprise-grade applications with Angular and RxJS.", "skills_covered": ["Angular", "TypeScript", "REST APIs"]},
        {"name": "Node.js Backend Mastery", "category": "Web Development", "difficulty": "Intermediate",
         "description": "Build scalable REST APIs and real-time apps with Node.js.", "skills_covered": ["Node.js", "Express.js", "REST APIs", "JavaScript"]},
        {"name": "Django Web Framework", "category": "Web Development", "difficulty": "Intermediate",
         "description": "Build robust web applications with Django and Python.", "skills_covered": ["Django", "Python", "Database Design", "REST APIs"]},
        {"name": "Flask Microservices", "category": "Web Development", "difficulty": "Intermediate",
         "description": "Create lightweight microservices with Flask and Docker.", "skills_covered": ["Flask", "Python", "Docker", "REST APIs", "Microservices"]},
        {"name": "HTML & CSS Masterclass", "category": "Web Development", "difficulty": "Beginner",
         "description": "From basics to advanced CSS Grid, Flexbox, and animations.", "skills_covered": ["HTML/CSS"]},
        {"name": "JavaScript Complete Guide", "category": "Web Development", "difficulty": "Beginner",
         "description": "Everything about JavaScript from fundamentals to ES2024 features.", "skills_covered": ["JavaScript"]},
        {"name": "GraphQL API Development", "category": "Web Development", "difficulty": "Advanced",
         "description": "Design and implement GraphQL APIs with Apollo Server.", "skills_covered": ["GraphQL", "Node.js", "JavaScript", "REST APIs"]},

        # ── Data Science (10) ────────────────────────────────────────
        {"name": "Introduction to Data Science", "category": "Data Science", "difficulty": "Beginner",
         "description": "Foundations of data science including data wrangling and EDA.", "skills_covered": ["Python", "Statistics", "Data Science", "Pandas"]},
        {"name": "Statistics for Data Science", "category": "Data Science", "difficulty": "Beginner",
         "description": "Probability, hypothesis testing, and statistical inference.", "skills_covered": ["Statistics", "Python", "Data Science"]},
        {"name": "Data Visualization Mastery", "category": "Data Science", "difficulty": "Intermediate",
         "description": "Create compelling visualizations with Matplotlib, Seaborn, and Plotly.", "skills_covered": ["Python", "Data Visualization", "Pandas", "Data Science"]},
        {"name": "Pandas & NumPy for Data Analysis", "category": "Data Science", "difficulty": "Intermediate",
         "description": "Efficient data manipulation and numerical computing in Python.", "skills_covered": ["Pandas", "NumPy", "Python", "Data Science"]},
        {"name": "SQL for Data Analysis", "category": "Data Science", "difficulty": "Beginner",
         "description": "Master SQL queries for extracting insights from relational databases.", "skills_covered": ["SQL", "Database Design", "Data Science"]},
        {"name": "Big Data with PySpark", "category": "Data Science", "difficulty": "Advanced",
         "description": "Process large-scale datasets with Apache Spark and Python.", "skills_covered": ["Python", "Data Science", "Cloud Computing"]},
        {"name": "Time Series Analysis", "category": "Data Science", "difficulty": "Advanced",
         "description": "Forecasting and anomaly detection in temporal data.", "skills_covered": ["Python", "Statistics", "Data Science", "Machine Learning"]},
        {"name": "Data Engineering Fundamentals", "category": "Data Science", "difficulty": "Intermediate",
         "description": "Build ETL pipelines and data warehouses.", "skills_covered": ["Python", "SQL", "Data Science", "Cloud Computing"]},
        {"name": "A/B Testing & Experimentation", "category": "Data Science", "difficulty": "Intermediate",
         "description": "Design and analyze experiments for product decisions.", "skills_covered": ["Statistics", "Python", "Data Science"]},
        {"name": "Linear Algebra for Data Science", "category": "Data Science", "difficulty": "Intermediate",
         "description": "Mathematical foundations for machine learning algorithms.", "skills_covered": ["Linear Algebra", "Statistics", "Python"]},

        # ── Machine Learning (10) ───────────────────────────────────
        {"name": "Machine Learning Foundations", "category": "Machine Learning", "difficulty": "Beginner",
         "description": "Supervised and unsupervised learning with scikit-learn.", "skills_covered": ["Python", "Machine Learning", "Statistics"]},
        {"name": "Deep Learning with TensorFlow", "category": "Machine Learning", "difficulty": "Advanced",
         "description": "Build neural networks for image and text processing.", "skills_covered": ["Python", "Deep Learning", "TensorFlow", "Machine Learning"]},
        {"name": "PyTorch for Deep Learning", "category": "Machine Learning", "difficulty": "Advanced",
         "description": "Dynamic neural networks and research-oriented deep learning.", "skills_covered": ["Python", "Deep Learning", "PyTorch", "Machine Learning"]},
        {"name": "Natural Language Processing", "category": "Machine Learning", "difficulty": "Advanced",
         "description": "Text classification, sentiment analysis, and language models.", "skills_covered": ["Python", "NLP", "Machine Learning", "Deep Learning"]},
        {"name": "Computer Vision with Python", "category": "Machine Learning", "difficulty": "Advanced",
         "description": "Image recognition, object detection, and segmentation.", "skills_covered": ["Python", "Computer Vision", "Deep Learning", "Machine Learning"]},
        {"name": "Recommendation Systems", "category": "Machine Learning", "difficulty": "Intermediate",
         "description": "Build collaborative and content-based recommendation engines.", "skills_covered": ["Python", "Machine Learning", "Statistics", "Linear Algebra"]},
        {"name": "Feature Engineering", "category": "Machine Learning", "difficulty": "Intermediate",
         "description": "Transform raw data into powerful predictive features.", "skills_covered": ["Python", "Machine Learning", "Data Science", "Pandas"]},
        {"name": "ML Model Deployment", "category": "Machine Learning", "difficulty": "Advanced",
         "description": "Deploy ML models with Flask, Docker, and cloud services.", "skills_covered": ["Python", "Machine Learning", "Docker", "Flask", "REST APIs"]},
        {"name": "Reinforcement Learning", "category": "Machine Learning", "difficulty": "Advanced",
         "description": "Train agents to make decisions in dynamic environments.", "skills_covered": ["Python", "Machine Learning", "Deep Learning", "Statistics"]},
        {"name": "Applied ML with Scikit-Learn", "category": "Machine Learning", "difficulty": "Intermediate",
         "description": "Practical machine learning pipelines for real-world problems.", "skills_covered": ["Python", "Machine Learning", "Statistics", "Pandas"]},

        # ── Cloud Computing (8) ──────────────────────────────────────
        {"name": "AWS Cloud Practitioner", "category": "Cloud Computing", "difficulty": "Beginner",
         "description": "Foundational understanding of AWS cloud services.", "skills_covered": ["AWS", "Cloud Computing"]},
        {"name": "AWS Solutions Architect", "category": "Cloud Computing", "difficulty": "Advanced",
         "description": "Design resilient, high-performing architectures on AWS.", "skills_covered": ["AWS", "Cloud Computing", "System Design", "Networking"]},
        {"name": "Azure Fundamentals", "category": "Cloud Computing", "difficulty": "Beginner",
         "description": "Get started with Microsoft Azure cloud services.", "skills_covered": ["Azure", "Cloud Computing"]},
        {"name": "Google Cloud Platform Essentials", "category": "Cloud Computing", "difficulty": "Beginner",
         "description": "Core GCP services and cloud-native development.", "skills_covered": ["GCP", "Cloud Computing"]},
        {"name": "Cloud Architecture Patterns", "category": "Cloud Computing", "difficulty": "Advanced",
         "description": "Design patterns for distributed cloud systems.", "skills_covered": ["Cloud Computing", "System Design", "Microservices"]},
        {"name": "Serverless Computing", "category": "Cloud Computing", "difficulty": "Intermediate",
         "description": "Build serverless applications with AWS Lambda and Azure Functions.", "skills_covered": ["AWS", "Azure", "Cloud Computing", "REST APIs"]},
        {"name": "Cloud Security Fundamentals", "category": "Cloud Computing", "difficulty": "Intermediate",
         "description": "Security best practices for cloud infrastructure.", "skills_covered": ["Cloud Computing", "Cybersecurity", "AWS"]},
        {"name": "Infrastructure as Code with Terraform", "category": "Cloud Computing", "difficulty": "Intermediate",
         "description": "Automate infrastructure provisioning with Terraform.", "skills_covered": ["Cloud Computing", "DevOps", "AWS", "Linux"]},

        # ── DevOps (7) ──────────────────────────────────────────────
        {"name": "Docker Complete Guide", "category": "DevOps", "difficulty": "Beginner",
         "description": "Containerize applications with Docker from scratch.", "skills_covered": ["Docker", "Linux", "DevOps"]},
        {"name": "Kubernetes in Production", "category": "DevOps", "difficulty": "Advanced",
         "description": "Orchestrate containers at scale with Kubernetes.", "skills_covered": ["Kubernetes", "Docker", "DevOps", "Cloud Computing"]},
        {"name": "CI/CD Pipeline Mastery", "category": "DevOps", "difficulty": "Intermediate",
         "description": "Build automated CI/CD pipelines with GitHub Actions and Jenkins.", "skills_covered": ["CI/CD", "Git", "DevOps", "Docker"]},
        {"name": "Linux System Administration", "category": "DevOps", "difficulty": "Intermediate",
         "description": "Master Linux for server management and automation.", "skills_covered": ["Linux", "DevOps"]},
        {"name": "Git Version Control", "category": "DevOps", "difficulty": "Beginner",
         "description": "Master Git workflows, branching strategies, and collaboration.", "skills_covered": ["Git", "DevOps"]},
        {"name": "Monitoring & Observability", "category": "DevOps", "difficulty": "Advanced",
         "description": "Implement monitoring with Prometheus, Grafana, and ELK stack.", "skills_covered": ["DevOps", "Linux", "Cloud Computing"]},
        {"name": "Site Reliability Engineering", "category": "DevOps", "difficulty": "Advanced",
         "description": "SRE practices for building reliable distributed systems.", "skills_covered": ["DevOps", "System Design", "Cloud Computing", "Linux"]},

        # ── Mobile Development (5) ──────────────────────────────────
        {"name": "React Native Mobile Apps", "category": "Mobile Development", "difficulty": "Intermediate",
         "description": "Build cross-platform mobile apps with React Native.", "skills_covered": ["React", "JavaScript", "REST APIs"]},
        {"name": "Flutter & Dart Complete", "category": "Mobile Development", "difficulty": "Intermediate",
         "description": "Create beautiful mobile applications with Flutter.", "skills_covered": ["HTML/CSS"]},
        {"name": "iOS Development with Swift", "category": "Mobile Development", "difficulty": "Intermediate",
         "description": "Build native iOS apps with Swift and SwiftUI.", "skills_covered": ["System Design"]},
        {"name": "Android Development with Kotlin", "category": "Mobile Development", "difficulty": "Intermediate",
         "description": "Create native Android applications with Kotlin.", "skills_covered": ["Java", "REST APIs"]},
        {"name": "Mobile App Security", "category": "Mobile Development", "difficulty": "Advanced",
         "description": "Secure mobile applications against common vulnerabilities.", "skills_covered": ["Cybersecurity"]},

        # ── Cybersecurity (6) ───────────────────────────────────────
        {"name": "Cybersecurity Essentials", "category": "Cybersecurity", "difficulty": "Beginner",
         "description": "Fundamentals of information security and threat landscape.", "skills_covered": ["Cybersecurity", "Networking"]},
        {"name": "Ethical Hacking & Penetration Testing", "category": "Cybersecurity", "difficulty": "Advanced",
         "description": "Offensive security techniques and vulnerability assessment.", "skills_covered": ["Cybersecurity", "Linux", "Networking"]},
        {"name": "Network Security", "category": "Cybersecurity", "difficulty": "Intermediate",
         "description": "Protect networks with firewalls, IDS/IPS, and encryption.", "skills_covered": ["Cybersecurity", "Networking"]},
        {"name": "Web Application Security", "category": "Cybersecurity", "difficulty": "Intermediate",
         "description": "OWASP Top 10 and securing web applications.", "skills_covered": ["Cybersecurity", "JavaScript", "REST APIs"]},
        {"name": "Cryptography Fundamentals", "category": "Cybersecurity", "difficulty": "Advanced",
         "description": "Encryption algorithms, PKI, and secure communication.", "skills_covered": ["Cybersecurity", "Statistics"]},
        {"name": "Security Operations Center", "category": "Cybersecurity", "difficulty": "Advanced",
         "description": "SOC operations, incident response, and threat hunting.", "skills_covered": ["Cybersecurity", "Linux", "Networking"]},

        # ── Database (5) ────────────────────────────────────────────
        {"name": "PostgreSQL Administration", "category": "Database", "difficulty": "Intermediate",
         "description": "Manage and optimize PostgreSQL databases.", "skills_covered": ["SQL", "Database Design", "Linux"]},
        {"name": "MongoDB Essentials", "category": "Database", "difficulty": "Beginner",
         "description": "NoSQL database design and operations with MongoDB.", "skills_covered": ["Database Design"]},
        {"name": "Redis for Caching & Messaging", "category": "Database", "difficulty": "Intermediate",
         "description": "In-memory data structures for high-performance apps.", "skills_covered": ["Database Design", "System Design"]},
        {"name": "Database Performance Tuning", "category": "Database", "difficulty": "Advanced",
         "description": "Query optimization, indexing strategies, and benchmarking.", "skills_covered": ["SQL", "Database Design", "System Design"]},
        {"name": "Data Modeling & Design", "category": "Database", "difficulty": "Intermediate",
         "description": "Relational and dimensional modeling for scalable databases.", "skills_covered": ["SQL", "Database Design"]},

        # ── Software Engineering (6) ────────────────────────────────
        {"name": "System Design Interview Prep", "category": "Software Engineering", "difficulty": "Advanced",
         "description": "Design scalable systems — load balancers, caches, and databases.", "skills_covered": ["System Design", "Database Design", "Cloud Computing"]},
        {"name": "Design Patterns in Python", "category": "Software Engineering", "difficulty": "Intermediate",
         "description": "Gang of Four patterns implemented in Python.", "skills_covered": ["Python", "System Design"]},
        {"name": "Agile & Scrum Mastery", "category": "Software Engineering", "difficulty": "Beginner",
         "description": "Agile methodologies, Scrum framework, and sprint planning.", "skills_covered": ["Agile"]},
        {"name": "Clean Code & Refactoring", "category": "Software Engineering", "difficulty": "Intermediate",
         "description": "Write maintainable code with SOLID principles.", "skills_covered": ["Python", "Java"]},
        {"name": "Microservices Architecture", "category": "Software Engineering", "difficulty": "Advanced",
         "description": "Design and build microservices-based distributed systems.", "skills_covered": ["Microservices", "Docker", "REST APIs", "System Design"]},
        {"name": "Software Testing & QA", "category": "Software Engineering", "difficulty": "Intermediate",
         "description": "Unit testing, integration testing, and test automation.", "skills_covered": ["Python", "JavaScript", "CI/CD"]},
    ]
    return courses


def generate_students(n_students=200):
    """
    Generate synthetic student profiles.
    
    Each student has 3-7 skills and 2-5 interests, sampled randomly.
    This creates diverse but realistic student profiles.
    
    Returns:
        List of dicts with keys: username, email, skills, interests
    """
    students = []
    first_names = [
        "Alex", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Quinn",
        "Avery", "Dakota", "Skyler", "Jamie", "Robin", "Sam", "Drew",
        "Peyton", "Reese", "Finley", "Rowan", "Sage", "Blake", "Charlie",
        "Emery", "Harper", "Hayden", "Kendall", "Logan", "Parker", "River",
        "Sawyer", "Spencer", "Ari", "Cameron", "Devon", "Ellis", "Francis",
        "Gray", "Harley", "Indigo", "Jules", "Kit",
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
        "Miller", "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor",
        "Thomas", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
        "Harris", "Clark", "Lewis", "Walker", "Hall", "Young", "Allen",
        "King", "Wright", "Scott", "Green", "Baker", "Adams", "Nelson",
        "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell",
    ]

    used_usernames = set()
    for i in range(n_students):
        while True:
            first = random.choice(first_names)
            last = random.choice(last_names)
            username = f"{first.lower()}.{last.lower()}{random.randint(1, 99)}"
            if username not in used_usernames:
                used_usernames.add(username)
                break

        n_skills = random.randint(3, 7)
        n_interests = random.randint(2, 5)

        students.append({
            "username": username,
            "email": f"{username}@example.com",
            "skills": random.sample(ALL_SKILLS, n_skills),
            "interests": random.sample(ALL_INTERESTS, n_interests),
        })

    return students


def compute_affinity(student, course):
    """
    Compute a base affinity score between a student and a course.
    
    Higher affinity when:
      - Student skills overlap with course skills_covered
      - Student interests relate to course category
      
    Returns a float in [0, 1] range.
    """
    student_skills = set(student["skills"])
    course_skills = set(course["skills_covered"])

    # Skill overlap ratio
    if len(course_skills) > 0:
        skill_overlap = len(student_skills & course_skills) / len(course_skills)
    else:
        skill_overlap = 0.0

    # Interest match: does the course category relate to any interest?
    interest_map = {
        "Web Development": ["Web Development", "Frontend Development", "Backend Development", "Full Stack"],
        "Data Science": ["AI/ML", "Data Engineering", "Data Visualization", "Research"],
        "Machine Learning": ["AI/ML", "Research", "Data Engineering"],
        "Cloud Computing": ["Cloud Computing", "DevOps"],
        "DevOps": ["DevOps", "Cloud Computing"],
        "Mobile Development": ["Mobile Development", "Full Stack"],
        "Cybersecurity": ["Cybersecurity"],
        "Database": ["Data Engineering", "Backend Development"],
        "Programming Fundamentals": ["Competitive Programming", "Open Source", "Full Stack"],
        "Software Engineering": ["Backend Development", "Full Stack", "Open Source"],
    }

    related_interests = interest_map.get(course["category"], [])
    interest_match = 1.0 if any(i in related_interests for i in student["interests"]) else 0.0

    # Combined affinity
    affinity = 0.6 * skill_overlap + 0.4 * interest_match
    return affinity


def generate_ratings(students, courses, target_ratings=3000):
    """
    Generate synthetic ratings with a realistic distribution.
    
    Ratings are NOT purely random — they correlate with skill/interest
    affinity, creating a learnable signal for the ML models.
    
    Rating formula:
      base_rating = 2.5 + 2.5 * affinity + noise
      clamped to [1, 5]
    
    Returns:
        List of dicts with keys: student_idx, course_idx, rating
    """
    ratings = []
    n_students = len(students)
    n_courses = len(courses)

    # Each student rates 10-25 courses (with some variance)
    for s_idx in range(n_students):
        n_rated = random.randint(10, 25)
        rated_courses = random.sample(range(n_courses), min(n_rated, n_courses))

        for c_idx in rated_courses:
            affinity = compute_affinity(students[s_idx], courses[c_idx])
            # Base rating influenced by affinity + Gaussian noise
            noise = np.random.normal(0, 0.7)
            base_rating = 2.0 + 2.5 * affinity + noise
            rating = round(max(1.0, min(5.0, base_rating)), 1)

            ratings.append({
                "student_idx": s_idx,
                "course_idx": c_idx,
                "rating": rating,
            })

            if len(ratings) >= target_ratings:
                return ratings

    return ratings
