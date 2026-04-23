"""
Evaluation module for the recommendation system.

Metrics:
  - RMSE (Root Mean Squared Error): Measures prediction accuracy.
    Lower is better. Computed on held-out test ratings.
    
  - Precision@K: Measures the fraction of top-K recommendations
    that are actually relevant (rated ≥ 4.0 by the user).
    Higher is better.
"""

import numpy as np
from typing import List, Tuple, Dict
from ml_model.collaborative import CollaborativeFilter
from ml_model.content_based import ContentBasedFilter
from ml_model.hybrid import HybridRecommender


def compute_rmse(predictions: List[Tuple[float, float]]) -> float:
    """
    Compute Root Mean Squared Error between predicted and actual ratings.
    
    Args:
        predictions: List of (predicted_rating, actual_rating) tuples
        
    Returns:
        RMSE value (float). Lower is better.
    """
    if not predictions:
        return 0.0

    squared_errors = [(pred - actual) ** 2 for pred, actual in predictions]
    mse = np.mean(squared_errors)
    return float(np.sqrt(mse))


def compute_precision_at_k(
    recommended_ids: List[int],
    relevant_ids: set,
    k: int = 5,
) -> float:
    """
    Compute Precision@K — fraction of top-K recommendations that are relevant.
    
    A course is "relevant" if the user rated it ≥ 4.0 in the test set.
    
    Args:
        recommended_ids: Ordered list of recommended course IDs (top first)
        relevant_ids: Set of course IDs rated ≥ 4.0 by the user
        k: Number of top recommendations to evaluate
        
    Returns:
        Precision@K value in [0.0, 1.0]. Higher is better.
    """
    if k <= 0:
        return 0.0

    top_k = recommended_ids[:k]
    hits = sum(1 for cid in top_k if cid in relevant_ids)
    return hits / k


def evaluate_model(
    hybrid_model: HybridRecommender,
    test_ratings: List[Tuple[int, int, float]],
    user_profiles: Dict[int, dict],
    k: int = 5,
) -> dict:
    """
    Run full evaluation on a hybrid model using held-out test data.
    
    Args:
        hybrid_model: Fitted HybridRecommender instance
        test_ratings: List of (user_id, course_id, actual_rating) from test set
        user_profiles: Dict mapping user_id -> {"skills": [...], "interests": [...]}
        k: K value for Precision@K
        
    Returns:
        Dict with keys: rmse, precision_at_k, n_predictions, n_users_evaluated
    """
    # Group test ratings by user
    user_test = {}
    for user_id, course_id, rating in test_ratings:
        if user_id not in user_test:
            user_test[user_id] = []
        user_test[user_id].append((course_id, rating))

    all_predictions = []     # (predicted, actual) pairs
    precision_scores = []    # Per-user Precision@K

    for user_id, test_items in user_test.items():
        profile = user_profiles.get(user_id)
        if profile is None:
            continue

        user_skills = profile.get("skills", [])
        user_interests = profile.get("interests", [])

        # Get test course IDs for this user
        test_course_ids = {cid for cid, _ in test_items}

        # Get recommendations (more than k to also evaluate RMSE)
        try:
            recs = hybrid_model.recommend(
                user_id=user_id,
                user_skills=user_skills,
                user_interests=user_interests,
                rated_course_ids=set(),  # Don't exclude test items for evaluation
                n=50,
            )
        except Exception:
            continue

        # Build prediction lookup
        pred_lookup = {r["course_id"]: r["predicted_score"] for r in recs}

        # ── RMSE: collect (predicted, actual) for test items ─────────
        for course_id, actual_rating in test_items:
            if course_id in pred_lookup:
                all_predictions.append((pred_lookup[course_id], actual_rating))

        # ── Precision@K ─────────────────────────────────────────────
        recommended_ids = [r["course_id"] for r in recs]
        # "Relevant" = rated ≥ 4.0 in test set
        relevant_ids = {cid for cid, rating in test_items if rating >= 4.0}
        if relevant_ids:
            p_at_k = compute_precision_at_k(recommended_ids, relevant_ids, k)
            precision_scores.append(p_at_k)

    rmse = compute_rmse(all_predictions)
    avg_precision = float(np.mean(precision_scores)) if precision_scores else 0.0

    return {
        "rmse": round(rmse, 4),
        "precision_at_k": round(avg_precision, 4),
        "k": k,
        "n_predictions": len(all_predictions),
        "n_users_evaluated": len(precision_scores),
    }
