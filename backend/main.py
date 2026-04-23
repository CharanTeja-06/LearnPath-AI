"""
FastAPI application for the Data-Driven Learning Path Recommendation System.
"""

import sys, os, json, random
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List

from database import (
    get_db, init_db, User, Course, Rating, Enrollment, PageProgress,
    SessionLocal, COURSE_TOTAL_PAGES,
)
from auth import hash_password, verify_password, create_access_token, get_current_user_id
from schemas import (
    UserSignup, UserLogin, TokenResponse, UserProfile,
    CourseResponse, RateCourseRequest,
    RecommendationItem, RecommendationResponse,
    EnrollRequest, PageCompleteRequest, PageInfo, EnrollmentInfo,
)
from seed_data import seed_database
from ml_model.hybrid import HybridRecommender
from ml_model.evaluation import evaluate_model

# ── Course content templates per category (5 pages each, unique per category) ──
CATEGORY_CONTENT = {
    "Web Development": [
        {"title": "HTML & CSS Foundations", "content": "Start with the building blocks of the web. Learn semantic HTML5 elements, CSS Box Model, Flexbox, Grid layouts, and responsive design principles. By the end of this module you'll be able to structure and style a complete webpage from scratch."},
        {"title": "JavaScript Essentials", "content": "Dive into JavaScript — the language that powers interactivity on the web. Cover variables, functions, DOM manipulation, event handling, ES6+ features like arrow functions, destructuring, and template literals."},
        {"title": "Frameworks & Libraries", "content": "Explore modern front-end frameworks including React, Vue, and Angular. Learn component architecture, state management, lifecycle hooks, and how to build Single Page Applications (SPAs)."},
        {"title": "Backend & APIs", "content": "Understand server-side development with Node.js, Express, or Django. Build RESTful APIs, handle authentication (JWT, OAuth), connect to databases, and implement CRUD operations."},
        {"title": "Deployment & DevOps", "content": "Take your projects live! Learn Git workflows, CI/CD pipelines, Docker containerization, cloud hosting (AWS, Vercel, Netlify), and monitoring production applications."},
    ],
    "Data Science": [
        {"title": "Data Exploration & Pandas", "content": "Begin your data science journey by learning how to load, clean, and explore datasets using Python and Pandas. Master DataFrames, filtering, grouping, merging, and handling missing values."},
        {"title": "Statistical Analysis", "content": "Understand descriptive and inferential statistics — mean, median, standard deviation, hypothesis testing, p-values, confidence intervals, and their practical applications in real-world data analysis."},
        {"title": "Data Visualization", "content": "Create compelling visual stories with Matplotlib, Seaborn, and Plotly. Learn chart types (bar, scatter, heatmap, box plots), dashboard design principles, and how to communicate insights effectively."},
        {"title": "Feature Engineering & Preprocessing", "content": "Transform raw data into model-ready features. Cover encoding categorical variables, scaling, normalization, handling outliers, dimensionality reduction (PCA), and cross-validation strategies."},
        {"title": "Capstone: End-to-End Project", "content": "Apply everything you've learned in a complete data science project — from defining a problem statement, collecting data, performing EDA, building models, to presenting findings and recommendations."},
    ],
    "Machine Learning": [
        {"title": "ML Fundamentals & Math", "content": "Build the mathematical foundation for ML — linear algebra, probability, calculus basics. Understand the bias-variance tradeoff, overfitting, underfitting, and the general ML pipeline from data to deployment."},
        {"title": "Supervised Learning", "content": "Master classification and regression algorithms including Linear/Logistic Regression, Decision Trees, Random Forests, SVMs, and k-NN. Learn how to evaluate models with accuracy, precision, recall, and F1-score."},
        {"title": "Unsupervised & Ensemble Methods", "content": "Explore clustering (K-Means, DBSCAN, Hierarchical), dimensionality reduction, and powerful ensemble methods like Gradient Boosting (XGBoost, LightGBM) and stacking strategies."},
        {"title": "Deep Learning & Neural Networks", "content": "Enter the world of deep learning with TensorFlow and PyTorch. Build feedforward networks, CNNs for images, RNNs/LSTMs for sequences, and understand backpropagation and optimization algorithms."},
        {"title": "Model Deployment & MLOps", "content": "Deploy your ML models to production. Learn model serialization (pickle, ONNX), REST API serving (FastAPI, Flask), model monitoring, A/B testing, and MLOps best practices."},
    ],
    "Cloud Computing": [
        {"title": "Cloud Fundamentals", "content": "Understand the cloud computing paradigm — IaaS, PaaS, SaaS models. Compare AWS, Azure, and GCP. Learn about virtual machines, storage types, networking basics, and the shared responsibility model."},
        {"title": "Compute & Networking", "content": "Deep dive into compute services (EC2, Lambda, Cloud Functions), load balancers, CDNs, VPCs, subnets, security groups, and how to architect scalable, highly available applications."},
        {"title": "Storage & Databases", "content": "Explore cloud storage options — object storage (S3), block storage, file storage. Learn managed databases (RDS, DynamoDB, Cosmos DB), caching (Redis, ElastiCache), and data lake architectures."},
        {"title": "Security & IAM", "content": "Master cloud security — Identity and Access Management (IAM), encryption at rest and in transit, VPN, key management, compliance frameworks, and security best practices for cloud-native apps."},
        {"title": "Infrastructure as Code", "content": "Automate your cloud infrastructure with Terraform, CloudFormation, and Pulumi. Learn declarative configurations, state management, modules, and how to implement GitOps workflows."},
    ],
    "DevOps": [
        {"title": "DevOps Culture & Principles", "content": "Understand the DevOps philosophy — breaking silos between Dev and Ops, continuous improvement, automation-first mindset, and the key metrics (DORA) that measure engineering excellence."},
        {"title": "CI/CD Pipelines", "content": "Build automated pipelines with Jenkins, GitHub Actions, and GitLab CI. Learn stages — build, test, deploy. Implement blue-green deployments, canary releases, and rollback strategies."},
        {"title": "Containerization & Docker", "content": "Master Docker from basics to production. Write efficient Dockerfiles, manage multi-container apps with Docker Compose, understand image layers, registries, and container security scanning."},
        {"title": "Kubernetes & Orchestration", "content": "Deploy and manage containers at scale with Kubernetes. Learn Pods, Services, Deployments, ConfigMaps, Secrets, Helm charts, and horizontal pod autoscaling for resilient applications."},
        {"title": "Monitoring & Observability", "content": "Implement full-stack observability with Prometheus, Grafana, ELK Stack, and Jaeger. Learn metrics, logging, distributed tracing, alerting strategies, and incident response workflows."},
    ],
    "Mobile Development": [
        {"title": "Mobile UI/UX Principles", "content": "Learn mobile-first design thinking — touch targets, gesture navigation, screen density, typography for small screens, Material Design and Human Interface Guidelines, and prototyping with Figma."},
        {"title": "Cross-Platform Fundamentals", "content": "Explore React Native, Flutter, and Kotlin Multiplatform. Understand the tradeoffs between native, hybrid, and cross-platform approaches and when to use each for maximum impact."},
        {"title": "State Management & Navigation", "content": "Master state management patterns (Redux, Provider, Riverpod, MobX) and navigation architectures (stack, tab, drawer). Handle deep linking, push notifications, and app lifecycle."},
        {"title": "APIs & Local Storage", "content": "Connect your mobile app to backend services. Implement REST/GraphQL clients, handle offline-first with SQLite/Hive, synchronize data, and manage authentication tokens securely."},
        {"title": "Publishing & Distribution", "content": "Prepare your app for the App Store and Google Play. Learn code signing, app review guidelines, beta testing (TestFlight, Firebase App Distribution), analytics, and crash reporting."},
    ],
    "Cybersecurity": [
        {"title": "Security Fundamentals", "content": "Learn the CIA triad (Confidentiality, Integrity, Availability), security models, threat landscapes, common attack vectors, and the OWASP Top 10 vulnerabilities that every developer should know."},
        {"title": "Network Security", "content": "Master firewalls, IDS/IPS, VPNs, SSL/TLS, DNS security, and network monitoring. Understand how attackers exploit network protocols and how to defend against common network attacks."},
        {"title": "Application Security", "content": "Secure your applications against SQL injection, XSS, CSRF, broken authentication, and insecure deserialization. Learn secure coding practices, input validation, and security testing tools."},
        {"title": "Cryptography & Authentication", "content": "Understand encryption (AES, RSA), hashing (SHA, bcrypt), digital signatures, PKI, OAuth 2.0/OIDC, multi-factor authentication, and zero-trust architecture principles."},
        {"title": "Incident Response & Forensics", "content": "Build your incident response playbook — detection, containment, eradication, recovery. Learn digital forensics basics, log analysis, threat intelligence, and compliance reporting."},
    ],
    "Database": [
        {"title": "Relational Database Design", "content": "Master database design — ER diagrams, normalization (1NF-3NF, BCNF), primary/foreign keys, constraints, and how to translate business requirements into efficient relational schemas."},
        {"title": "SQL Mastery", "content": "Write powerful SQL queries — JOINs, subqueries, CTEs, window functions, aggregations, and recursive queries. Cover DDL, DML, DCL operations and query optimization techniques."},
        {"title": "NoSQL & Document Databases", "content": "Explore MongoDB, Redis, Cassandra, and Neo4j. Understand document, key-value, wide-column, and graph database models. Learn when to choose SQL vs NoSQL for your use case."},
        {"title": "Performance & Indexing", "content": "Optimize database performance with proper indexing strategies (B-tree, Hash, GIN, GiST), query execution plans (EXPLAIN), connection pooling, partitioning, and caching layers."},
        {"title": "Replication & Sharding", "content": "Scale your database horizontally and vertically. Learn master-slave replication, multi-master setups, sharding strategies, consistent hashing, and CAP theorem implications."},
    ],
    "Programming Fundamentals": [
        {"title": "Variables, Types & Control Flow", "content": "Start from the very beginning — variables, data types (int, float, string, bool), operators, conditional statements (if/else), loops (for, while), and writing clean, readable code."},
        {"title": "Functions & Data Structures", "content": "Learn to organize code with functions — parameters, return values, scope. Master essential data structures: arrays, linked lists, stacks, queues, hash maps, and when to use each."},
        {"title": "Object-Oriented Programming", "content": "Understand OOP pillars — encapsulation, inheritance, polymorphism, abstraction. Design classes, interfaces, use design patterns (Singleton, Factory, Observer), and write SOLID code."},
        {"title": "Algorithms & Complexity", "content": "Analyze algorithm efficiency with Big-O notation. Implement sorting (merge, quick, heap), searching (binary search, BFS, DFS), dynamic programming, and greedy algorithms."},
        {"title": "Version Control & Collaboration", "content": "Master Git and GitHub — commits, branches, merging, rebasing, pull requests, code reviews. Learn collaborative workflows and how to contribute to open-source projects."},
    ],
    "Software Engineering": [
        {"title": "Software Development Lifecycle", "content": "Understand SDLC models — Waterfall, Agile (Scrum, Kanban), and Lean. Learn how to gather requirements, write user stories, estimate tasks, and manage sprints effectively."},
        {"title": "System Design Fundamentals", "content": "Design scalable systems from scratch. Learn load balancing, caching strategies, message queues, microservices vs monolith, API gateways, and rate limiting architectures."},
        {"title": "Testing & Quality Assurance", "content": "Write robust tests — unit tests, integration tests, E2E tests. Use testing frameworks (Jest, pytest, JUnit). Learn TDD, BDD, mocking, code coverage, and testing pyramid strategies."},
        {"title": "Clean Code & Architecture", "content": "Write maintainable code following Clean Code principles. Understand architectural patterns — MVC, MVVM, hexagonal, event-driven. Apply SOLID, DRY, KISS principles daily."},
        {"title": "Technical Documentation", "content": "Create effective documentation — API docs (OpenAPI/Swagger), README files, architecture decision records (ADRs), runbooks, and onboarding guides that help teams scale faster."},
    ],
}

# Fallback for unknown categories
DEFAULT_CONTENT = [
    {"title": "Introduction & Overview",         "content": "Welcome to this course! This module covers the foundational concepts, learning objectives, and roadmap for what you will master by the end of the program."},
    {"title": "Core Concepts & Theory",          "content": "In this module we dive deep into the core theoretical concepts. Understand the principles and frameworks that form the backbone of this subject area."},
    {"title": "Hands-On Practice",               "content": "Time to get your hands dirty! This module contains practical exercises, coding challenges, and guided labs to reinforce your understanding."},
    {"title": "Advanced Topics & Best Practices", "content": "Now that you have the basics, explore advanced patterns, optimization techniques, and industry best practices used by professionals."},
    {"title": "Final Assessment & Next Steps",    "content": "Congratulations on reaching the final module! Complete the assessment to validate your knowledge and discover recommended next courses."},
]

# Priority reasons for recommendations
PRIORITY_REASONS = {
    1: "🥇 Top Pick — Highest predicted match for your learning profile",
    2: "🥈 Strong Match — Closely aligns with your skills and interests",
    3: "🥉 Great Fit — Recommended by learners similar to you",
    4: "⭐ Skill Builder — Fills a key gap in your skill portfolio",
    5: "📈 Growth Pick — Expands your knowledge into adjacent areas",
    6: "🎯 Trending — Popular among learners in your category",
    7: "🔗 Connected — Builds on courses you've already excelled in",
    8: "💡 Explorer — Introduces you to a new and valuable domain",
    9: "🧩 Complement — Complements your existing course portfolio",
    10: "🌱 Horizon — Broadens your overall learning trajectory",
}


def get_course_pages(category: str):
    """Get 5-page content templates for a given course category."""
    return CATEGORY_CONTENT.get(category, DEFAULT_CONTENT)


app = FastAPI(title="Learning Path Recommendation System", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

recommender: Optional[HybridRecommender] = None

DIFFICULTY_ORDER = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}


def train_recommender():
    global recommender
    db = SessionLocal()
    try:
        ratings = db.query(Rating).all()
        if len(ratings) < 10:
            print("Not enough ratings to train model.")
            return
        ratings_data = [(r.user_id, r.course_id, r.rating) for r in ratings]
        user_ids = sorted(set(r.user_id for r in ratings))
        course_ids = sorted(set(r.course_id for r in ratings))
        courses = db.query(Course).all()
        courses_info = [{"id": c.id, "name": c.name, "category": c.category,
                         "difficulty": c.difficulty, "description": c.description,
                         "skills_covered": json.loads(c.skills_covered) if c.skills_covered else []}
                        for c in courses]
        model = HybridRecommender(alpha=0.6)
        model.fit(ratings_data, user_ids, course_ids, courses_info)
        recommender = model
        print(f"[OK] Recommendation engine trained on {len(ratings_data)} ratings")
    except Exception as e:
        print(f"Error training recommender: {e}")
        import traceback; traceback.print_exc()
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    print("\n>> Starting Learning Path Recommendation System...")
    init_db()
    seed_database()
    train_recommender()
    print("[OK] System ready!\n")


# ═══════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════
@app.post("/signup", response_model=TokenResponse)
def signup(data: UserSignup, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already registered")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Username already taken")
    user = User(username=data.username, email=data.email,
                hashed_password=hash_password(data.password),
                skills=json.dumps(data.skills), interests=json.dumps(data.interests))
    db.add(user); db.commit(); db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user_id=user.id, username=user.username)

@app.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid email or password")
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user_id=user.id, username=user.username)

@app.get("/profile", response_model=UserProfile)
def get_profile(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")
    return UserProfile(id=user.id, username=user.username, email=user.email,
                       skills=json.loads(user.skills) if user.skills else [],
                       interests=json.loads(user.interests) if user.interests else [])


# ═══════════════════════════════════════════════════════════════════════════
# COURSES
# ═══════════════════════════════════════════════════════════════════════════
@app.get("/courses")
def list_courses(
    search: Optional[str] = None, category: Optional[str] = None,
    difficulty: Optional[str] = None, db: Session = Depends(get_db),
):
    query = db.query(Course)
    if search: query = query.filter(Course.name.ilike(f"%{search}%"))
    if category: query = query.filter(Course.category == category)
    if difficulty: query = query.filter(Course.difficulty == difficulty)
    courses = query.all()
    result = []
    for c in courses:
        avg = db.query(func.avg(Rating.rating)).filter(Rating.course_id == c.id).scalar()
        result.append({
            "id": c.id, "name": c.name, "category": c.category,
            "difficulty": c.difficulty, "description": c.description,
            "skills_covered": json.loads(c.skills_covered) if c.skills_covered else [],
            "avg_rating": round(float(avg), 2) if avg else None,
            "total_pages": COURSE_TOTAL_PAGES,
        })
    return result

@app.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    return [c[0] for c in db.query(Course.category).distinct().all()]


# ═══════════════════════════════════════════════════════════════════════════
# RATINGS
# ═══════════════════════════════════════════════════════════════════════════
@app.post("/rate-course")
def rate_course(data: RateCourseRequest, user_id: int = Depends(get_current_user_id),
                db: Session = Depends(get_db)):
    if not 1.0 <= data.rating <= 5.0:
        raise HTTPException(400, "Rating must be between 1 and 5")
    course = db.query(Course).filter(Course.id == data.course_id).first()
    if not course: raise HTTPException(404, "Course not found")
    existing = db.query(Rating).filter(Rating.user_id == user_id, Rating.course_id == data.course_id).first()
    if existing:
        existing.rating = data.rating
    else:
        db.add(Rating(user_id=user_id, course_id=data.course_id, rating=data.rating))
    db.commit()
    train_recommender()
    return {"message": "Rating submitted", "rating": data.rating}


# ═══════════════════════════════════════════════════════════════════════════
# ENROLLMENT & PROGRESS
# ═══════════════════════════════════════════════════════════════════════════
@app.post("/enroll")
def enroll_course(data: EnrollRequest, user_id: int = Depends(get_current_user_id),
                  db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == data.course_id).first()
    if not course: raise HTTPException(404, "Course not found")
    existing = db.query(Enrollment).filter(
        Enrollment.user_id == user_id, Enrollment.course_id == data.course_id).first()
    if existing:
        raise HTTPException(400, "Already enrolled")
    enrollment = Enrollment(user_id=user_id, course_id=data.course_id)
    db.add(enrollment); db.flush()
    # Create 5 page progress entries
    for i in range(1, COURSE_TOTAL_PAGES + 1):
        db.add(PageProgress(enrollment_id=enrollment.id, page_number=i, completed=False))
    db.commit()
    return {"message": f"Enrolled in {course.name}", "enrollment_id": enrollment.id}


@app.delete("/unenroll/{course_id}")
def unenroll_course(course_id: int, user_id: int = Depends(get_current_user_id),
                    db: Session = Depends(get_db)):
    """Drop / unenroll from a course. Removes enrollment and all page progress."""
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == user_id, Enrollment.course_id == course_id).first()
    if not enrollment:
        raise HTTPException(404, "Not enrolled in this course")
    # Delete page progress first (cascade should handle, but explicit is safe)
    db.query(PageProgress).filter(PageProgress.enrollment_id == enrollment.id).delete()
    db.delete(enrollment)
    db.commit()
    return {"message": "Successfully dropped the course", "course_id": course_id}


@app.get("/enrollments")
def get_enrollments(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    enrollments = db.query(Enrollment).filter(Enrollment.user_id == user_id).all()
    result = []
    for e in enrollments:
        course = db.query(Course).filter(Course.id == e.course_id).first()
        pages = db.query(PageProgress).filter(PageProgress.enrollment_id == e.id).all()
        completed = sum(1 for p in pages if p.completed)
        total = len(pages) or COURSE_TOTAL_PAGES
        result.append({
            "enrollment_id": e.id, "course_id": e.course_id,
            "course_name": course.name if course else "", "category": course.category if course else "",
            "difficulty": course.difficulty if course else "",
            "description": course.description if course else "",
            "total_pages": total, "completed_pages": completed,
            "progress_percent": round((completed / total) * 100, 1) if total > 0 else 0,
            "enrolled_at": e.enrolled_at.isoformat() if e.enrolled_at else None,
        })
    # Sort by difficulty: Beginner -> Intermediate -> Advanced
    result.sort(key=lambda x: DIFFICULTY_ORDER.get(x["difficulty"], 99))
    return result


@app.get("/course-content/{course_id}")
def get_course_content(course_id: int, user_id: int = Depends(get_current_user_id),
                       db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course: raise HTTPException(404, "Course not found")
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == user_id, Enrollment.course_id == course_id).first()
    if not enrollment: raise HTTPException(403, "Not enrolled in this course")
    pages = db.query(PageProgress).filter(
        PageProgress.enrollment_id == enrollment.id).order_by(PageProgress.page_number).all()
    skills = json.loads(course.skills_covered) if course.skills_covered else []

    # Get category-specific content
    content_templates = get_course_pages(course.category)

    page_list = []
    for p in pages:
        tpl = content_templates[p.page_number - 1] if p.page_number <= len(content_templates) else {"title": f"Page {p.page_number}", "content": ""}
        page_list.append({
            "page_number": p.page_number, "title": tpl["title"],
            "content": tpl["content"], "completed": p.completed,
        })
    completed_count = sum(1 for p in pages if p.completed)
    return {
        "course_id": course.id, "course_name": course.name,
        "category": course.category, "difficulty": course.difficulty,
        "description": course.description, "skills_covered": skills,
        "pages": page_list, "total_pages": len(pages),
        "completed_pages": completed_count,
        "progress_percent": round((completed_count / len(pages)) * 100, 1) if pages else 0,
    }


@app.post("/complete-page")
def complete_page(data: PageCompleteRequest, user_id: int = Depends(get_current_user_id),
                  db: Session = Depends(get_db)):
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == user_id, Enrollment.course_id == data.course_id).first()
    if not enrollment: raise HTTPException(403, "Not enrolled")
    page = db.query(PageProgress).filter(
        PageProgress.enrollment_id == enrollment.id, PageProgress.page_number == data.page_number).first()
    if not page: raise HTTPException(404, "Page not found")
    page.completed = True
    page.completed_at = datetime.utcnow()
    db.commit()
    # Return updated progress
    pages = db.query(PageProgress).filter(PageProgress.enrollment_id == enrollment.id).all()
    completed = sum(1 for p in pages if p.completed)
    total = len(pages)
    return {"message": "Page completed", "completed_pages": completed, "total_pages": total,
            "progress_percent": round((completed / total) * 100, 1) if total > 0 else 0}


# ═══════════════════════════════════════════════════════════════════════════
# RECOMMENDATIONS (sorted Beginner -> Advanced, with priority rank)
# ═══════════════════════════════════════════════════════════════════════════
@app.get("/recommendations/{target_user_id}")
def get_recommendations(target_user_id: int, db: Session = Depends(get_db)):
    global recommender
    user = db.query(User).filter(User.id == target_user_id).first()
    if not user: raise HTTPException(404, "User not found")
    user_skills = json.loads(user.skills) if user.skills else []
    user_interests = json.loads(user.interests) if user.interests else []
    rated = {r[0] for r in db.query(Rating.course_id).filter(Rating.user_id == target_user_id).all()}
    if recommender is None:
        raise HTTPException(503, "Recommendation engine is not ready.")
    recs = recommender.recommend(user_id=target_user_id, user_skills=user_skills,
                                 user_interests=user_interests, rated_course_ids=rated, n=10)
    # Sort by difficulty order: Beginner first, then Intermediate, then Advanced
    recs.sort(key=lambda r: DIFFICULTY_ORDER.get(r["difficulty"], 99))
    # Also check enrollment status for each
    enrolled_ids = {e.course_id for e in db.query(Enrollment).filter(Enrollment.user_id == target_user_id).all()}
    for i, r in enumerate(recs):
        r["is_enrolled"] = r["course_id"] in enrolled_ids
        r["priority"] = i + 1
        r["priority_reason"] = PRIORITY_REASONS.get(i + 1, "📚 Recommended for your continued growth")
    return {"user_id": target_user_id, "recommendations": recs,
            "model_info": recommender.get_model_info()}


# ═══════════════════════════════════════════════════════════════════════════
# USER STATS
# ═══════════════════════════════════════════════════════════════════════════
@app.get("/user-stats/{target_user_id}")
def get_user_stats(target_user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == target_user_id).first()
    if not user: raise HTTPException(404, "User not found")
    ratings = db.query(Rating).filter(Rating.user_id == target_user_id).all()
    enrollments = db.query(Enrollment).filter(Enrollment.user_id == target_user_id).all()
    total_enrolled = len(enrollments)
    total_progress = 0
    for e in enrollments:
        pages = db.query(PageProgress).filter(PageProgress.enrollment_id == e.id).all()
        if pages:
            total_progress += sum(1 for p in pages if p.completed) / len(pages)
    avg_progress = round((total_progress / total_enrolled) * 100, 1) if total_enrolled > 0 else 0
    if not ratings:
        return {"ratings_by_category": [], "rating_distribution": [],
                "total_courses_rated": 0, "average_rating": 0,
                "total_enrolled": total_enrolled, "avg_progress": avg_progress}
    category_ratings = {}
    for r in ratings:
        course = db.query(Course).filter(Course.id == r.course_id).first()
        if course:
            cat = course.category
            if cat not in category_ratings: category_ratings[cat] = {"total": 0, "count": 0}
            category_ratings[cat]["total"] += r.rating
            category_ratings[cat]["count"] += 1
    ratings_by_category = [{"category": cat, "avg_rating": round(d["total"]/d["count"], 2), "count": d["count"]}
                           for cat, d in category_ratings.items()]
    dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in ratings:
        b = max(1, min(5, int(round(r.rating))))
        dist[b] += 1
    rating_distribution = [{"stars": s, "count": c} for s, c in sorted(dist.items())]
    avg = sum(r.rating for r in ratings) / len(ratings)
    return {"ratings_by_category": ratings_by_category, "rating_distribution": rating_distribution,
            "total_courses_rated": len(ratings), "average_rating": round(avg, 2),
            "total_enrolled": total_enrolled, "avg_progress": avg_progress}


@app.get("/evaluation")
def get_evaluation(db: Session = Depends(get_db)):
    global recommender
    if recommender is None: raise HTTPException(503, "Model not ready")
    ratings = db.query(Rating).all()
    all_ratings = [(r.user_id, r.course_id, r.rating) for r in ratings]
    random.shuffle(all_ratings)
    split = int(len(all_ratings) * 0.8)
    test_ratings = all_ratings[split:]
    users = db.query(User).all()
    user_profiles = {u.id: {"skills": json.loads(u.skills) if u.skills else [],
                            "interests": json.loads(u.interests) if u.interests else []} for u in users}
    results = evaluate_model(recommender, test_ratings, user_profiles, k=5)
    results["model_info"] = recommender.get_model_info()
    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
