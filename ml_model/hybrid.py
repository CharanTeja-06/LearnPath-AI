"""
Hybrid Recommendation Engine combining Collaborative and Content-Based Filtering.

Scoring formula:
  Final_Score = α * CF_Score + (1 - α) * CBF_Score
  
  Where α = 0.6 (collaborative filtering weight)

This hybrid approach mitigates the weaknesses of each individual method:
  - CF suffers from cold-start for new users → CBF fills the gap using profile data
  - CBF can create "filter bubbles" → CF brings diversity from peer preferences

The explanation string tells the user WHY a course was recommended,
combining signals from both models.
"""

import json
from typing import List, Dict, Tuple, Optional

from ml_model.collaborative import CollaborativeFilter
from ml_model.content_based import ContentBasedFilter


# Weight for collaborative filtering (CF). Content-based gets 1 - ALPHA.
ALPHA = 0.6


class HybridRecommender:
    """
    Hybrid recommendation engine that merges CF and CBF predictions.
    
    Attributes:
        cf_model (CollaborativeFilter): Collaborative filtering model
        cbf_model (ContentBasedFilter): Content-based filtering model
        alpha (float): Weight for CF scores (default 0.6)
        courses_by_id (dict): Quick lookup for course metadata
    """

    def __init__(self, alpha=ALPHA):
        self.cf_model = CollaborativeFilter(n_neighbors=20)
        self.cbf_model = ContentBasedFilter()
        self.alpha = alpha
        self.courses_by_id = {}
        self._is_fitted = False

    def fit(self, ratings_data, user_ids, course_ids, courses_info):
        """
        Train both sub-models.
        
        Args:
            ratings_data: List of (user_id, course_id, rating) tuples
            user_ids: List of all unique user IDs
            course_ids: List of all unique course IDs
            courses_info: List of course dicts (id, name, category, etc.)
        """
        # Store course metadata for explanations
        self.courses_by_id = {c["id"]: c for c in courses_info}

        # ── Train Collaborative Filtering ────────────────────────────
        self.cf_model.build_matrix(ratings_data, user_ids, course_ids)
        self.cf_model.fit()

        # ── Train Content-Based Filtering ────────────────────────────
        self.cbf_model.fit(courses_info)

        self._is_fitted = True

    def recommend(
        self,
        user_id: int,
        user_skills: List[str],
        user_interests: List[str],
        rated_course_ids: Optional[set] = None,
        n: int = 5,
    ) -> List[Dict]:
        """
        Generate top-N hybrid recommendations.
        
        Steps:
          1. Get CF predictions for all unrated courses
          2. Get CBF predictions for all unrated courses
          3. Normalize both score sets to [0, 1] range
          4. Combine: final = α * CF_norm + (1-α) * CBF_norm
          5. Scale back to [1, 5] rating range
          6. Sort and return top N with explanations
        
        Args:
            user_id: Target user's database ID
            user_skills: User's skill list
            user_interests: User's interest list
            rated_course_ids: Set of already-rated course IDs to exclude
            n: Number of recommendations to return (default 5)
            
        Returns:
            List of recommendation dicts with keys:
              course_id, course_name, category, difficulty,
              predicted_score, explanation
        """
        if not self._is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")

        if rated_course_ids is None:
            rated_course_ids = set()

        # ── Step 1: Collaborative Filtering predictions ──────────────
        cf_predictions = self.cf_model.predict_for_user(user_id)

        # ── Step 2: Content-Based Filtering predictions ──────────────
        cbf_predictions = self.cbf_model.predict_for_user(
            user_skills, user_interests, rated_course_ids
        )

        # ── Step 3: Merge predictions ────────────────────────────────
        # Get the union of all predicted course IDs
        all_course_ids = set(cf_predictions.keys()) | set(cbf_predictions.keys())
        # Remove already rated courses
        all_course_ids -= rated_course_ids

        if not all_course_ids:
            return []

        # Normalize CF scores to [0, 1]
        cf_scores = {cid: cf_predictions.get(cid, 0) for cid in all_course_ids}
        cbf_scores = {cid: cbf_predictions.get(cid, 0) for cid in all_course_ids}

        cf_values = list(cf_scores.values())
        cbf_values = list(cbf_scores.values())

        cf_min, cf_max = min(cf_values) if cf_values else 0, max(cf_values) if cf_values else 1
        cbf_min, cbf_max = min(cbf_values) if cbf_values else 0, max(cbf_values) if cbf_values else 1

        cf_range = cf_max - cf_min if cf_max != cf_min else 1.0
        cbf_range = cbf_max - cbf_min if cbf_max != cbf_min else 1.0

        # ── Step 4: Compute hybrid scores ────────────────────────────
        hybrid_scores = {}
        for cid in all_course_ids:
            cf_norm = (cf_scores[cid] - cf_min) / cf_range
            cbf_norm = (cbf_scores[cid] - cbf_min) / cbf_range

            # Weighted combination
            hybrid_norm = self.alpha * cf_norm + (1 - self.alpha) * cbf_norm
            # Scale back to 1-5 range
            final_score = 1.0 + 4.0 * hybrid_norm
            hybrid_scores[cid] = round(max(1.0, min(5.0, final_score)), 2)

        # ── Step 5: Sort and take top N ──────────────────────────────
        sorted_scores = sorted(
            hybrid_scores.items(), key=lambda x: x[1], reverse=True
        )[:n]

        # ── Step 6: Build response with explanations ─────────────────
        recommendations = []
        for course_id, score in sorted_scores:
            course = self.courses_by_id.get(course_id, {})
            explanation = self._generate_explanation(
                course_id, course, cf_scores.get(course_id, 0),
                cbf_scores.get(course_id, 0), user_skills, user_interests
            )

            recommendations.append({
                "course_id": course_id,
                "course_name": course.get("name", "Unknown"),
                "category": course.get("category", ""),
                "difficulty": course.get("difficulty", ""),
                "predicted_score": score,
                "explanation": explanation,
            })

        return recommendations

    def _generate_explanation(
        self, course_id, course, cf_score, cbf_score,
        user_skills, user_interests
    ) -> str:
        """
        Generate a human-readable explanation for why a course was recommended.
        
        Explains the contribution of both CF and CBF signals.
        """
        explanations = []

        # ── CF contribution ──────────────────────────────────────────
        if cf_score > 0:
            explanations.append(
                "Similar learners who share your learning patterns rated this course highly"
            )

        # ── CBF contribution ─────────────────────────────────────────
        course_skills = course.get("skills_covered", [])
        if isinstance(course_skills, str):
            course_skills = json.loads(course_skills)

        matching_skills = set(user_skills) & set(course_skills)
        if matching_skills:
            skills_str = ", ".join(list(matching_skills)[:3])
            explanations.append(
                f"Matches your skills in {skills_str}"
            )

        # Check interest-category alignment
        category = course.get("category", "")
        interest_category_map = {
            "Web Development": ["Web Development", "Frontend Development", "Backend Development", "Full Stack"],
            "Data Science": ["AI/ML", "Data Engineering", "Data Visualization", "Research"],
            "Machine Learning": ["AI/ML", "Research"],
            "Cloud Computing": ["Cloud Computing", "DevOps"],
            "DevOps": ["DevOps", "Cloud Computing"],
            "Mobile Development": ["Mobile Development"],
            "Cybersecurity": ["Cybersecurity"],
            "Database": ["Data Engineering", "Backend Development"],
            "Programming Fundamentals": ["Competitive Programming", "Open Source"],
            "Software Engineering": ["Backend Development", "Full Stack"],
        }
        related = interest_category_map.get(category, [])
        matching_interests = [i for i in user_interests if i in related]
        if matching_interests:
            explanations.append(
                f"Aligns with your interest in {matching_interests[0]}"
            )

        if not explanations:
            explanations.append(
                "Recommended based on your overall learning profile and peer activity"
            )

        return ". ".join(explanations) + "."

    def get_model_info(self) -> dict:
        """Return metadata about the model configuration."""
        return {
            "algorithm": "Hybrid (Collaborative + Content-Based)",
            "cf_weight": self.alpha,
            "cbf_weight": 1 - self.alpha,
            "cf_method": "KNN with cosine similarity",
            "cbf_method": "TF-IDF vectorization + cosine similarity",
            "n_neighbors": self.cf_model.n_neighbors,
        }
