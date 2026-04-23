"""
Content-Based Filtering (CBF) module using TF-IDF vectorization.

How it works:
  1. Create a text profile for each user from their skills + interests
  2. Create a text profile for each course from its skills_covered +
     category + difficulty + description
  3. Apply TF-IDF vectorization to convert text profiles into numerical vectors
  4. Compute cosine similarity between the user profile vector and every
     course profile vector
  5. Rank courses by similarity — higher similarity means better match

This approach recommends courses whose content matches the student's
declared skills and interests, regardless of what other users have done.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedFilter:
    """
    Content-Based Filtering with TF-IDF and cosine similarity.
    
    Attributes:
        vectorizer (TfidfVectorizer): Fitted TF-IDF model
        course_profiles (list): Text profiles for each course
        course_vectors (np.ndarray): TF-IDF matrix for courses
        course_ids (list): Mapping from index to course ID
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=500,
            ngram_range=(1, 2),  # Unigrams and bigrams for richer features
        )
        self.course_profiles = []
        self.course_vectors = None
        self.course_ids = []
        self.course_data = {}  # course_id -> course info dict

    def _build_course_profile(self, course):
        """
        Build a text profile for a course by concatenating its metadata.
        
        Includes:
          - Category (weighted by repetition for emphasis)
          - Difficulty level
          - Skills covered
          - Description
          
        Example output:
          "Web Development Web Development Intermediate React JavaScript
           HTML CSS Build dynamic UIs with React hooks"
        """
        parts = []
        # Repeat category for emphasis (it's a strong signal)
        parts.append(course["category"])
        parts.append(course["category"])
        parts.append(course["difficulty"])
        # Add each skill
        skills = course.get("skills_covered", [])
        if isinstance(skills, str):
            import json
            skills = json.loads(skills)
        parts.extend(skills)
        # Add description
        parts.append(course.get("description", ""))
        return " ".join(parts)

    def _build_user_profile(self, user_skills, user_interests):
        """
        Build a text profile for a user from their skills and interests.
        
        Skills are weighted more heavily (repeated) because they indicate
        actual competence, while interests indicate aspiration.
        
        Example output:
          "Python Python Machine Learning Machine Learning Data Science
           AI ML Research"
        """
        parts = []
        # Repeat skills for stronger weighting
        for skill in user_skills:
            parts.append(skill)
            parts.append(skill)  # Double weight
        # Interests at normal weight
        parts.extend(user_interests)
        return " ".join(parts)

    def fit(self, courses):
        """
        Fit the TF-IDF vectorizer on course profiles.
        
        Args:
            courses: List of dicts with keys: id, name, category,
                     difficulty, description, skills_covered
        """
        self.course_ids = [c["id"] for c in courses]
        self.course_data = {c["id"]: c for c in courses}
        self.course_profiles = [self._build_course_profile(c) for c in courses]

        # Fit TF-IDF on course profiles
        self.course_vectors = self.vectorizer.fit_transform(self.course_profiles)

    def predict_for_user(self, user_skills, user_interests, rated_course_ids=None):
        """
        Predict relevance scores for all courses for a given user.
        
        Algorithm:
          1. Build user text profile from skills + interests
          2. Transform with the fitted TF-IDF vectorizer
          3. Compute cosine similarity against all course vectors
          4. Scale similarities to 1-5 rating range
          
        Args:
            user_skills: List of skill strings
            user_interests: List of interest strings
            rated_course_ids: Set of course IDs to exclude (already rated)
            
        Returns:
            Dict mapping course_id -> predicted_score (1.0 to 5.0)
        """
        if rated_course_ids is None:
            rated_course_ids = set()

        user_profile = self._build_user_profile(user_skills, user_interests)

        # Transform user profile using the fitted vectorizer
        user_vector = self.vectorizer.transform([user_profile])

        # Compute cosine similarity between user and all courses
        similarities = cosine_similarity(user_vector, self.course_vectors).flatten()

        predictions = {}
        for idx, course_id in enumerate(self.course_ids):
            if course_id in rated_course_ids:
                continue
            # Scale similarity [0, 1] to rating range [1, 5]
            score = 1.0 + 4.0 * similarities[idx]
            predictions[course_id] = round(max(1.0, min(5.0, score)), 2)

        return predictions

    def get_top_n(self, user_skills, user_interests, rated_course_ids=None, n=5):
        """
        Get top-N course recommendations based on content similarity.
        
        Returns:
            List of (course_id, predicted_score) sorted by score desc
        """
        predictions = self.predict_for_user(
            user_skills, user_interests, rated_course_ids
        )
        sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        return sorted_preds[:n]
