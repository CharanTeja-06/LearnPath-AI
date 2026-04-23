"""
Collaborative Filtering (CF) module using K-Nearest Neighbors.

How it works:
  1. Build a user-item rating matrix from the database
  2. Use sklearn's NearestNeighbors with cosine similarity to find
     K users most similar to the target user
  3. For each unseen course, predict the rating as a weighted average
     of the neighbor ratings (weighted by similarity)

This is a user-based collaborative filtering approach — it recommends
courses that similar users have rated highly.
"""

import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity


class CollaborativeFilter:
    """
    User-based Collaborative Filtering with KNN.
    
    Attributes:
        n_neighbors (int): Number of similar users to consider
        user_item_matrix (np.ndarray): Shape (n_users, n_courses), 0 = unrated
        user_ids (list): Mapping from matrix row index to user ID
        course_ids (list): Mapping from matrix column index to course ID
        knn_model (NearestNeighbors): Fitted KNN model
    """

    def __init__(self, n_neighbors=20):
        self.n_neighbors = n_neighbors
        self.user_item_matrix = None
        self.user_ids = []
        self.course_ids = []
        self.knn_model = None
        self.user_means = None  # Per-user mean rating for normalization

    def build_matrix(self, ratings_data, user_ids, course_ids):
        """
        Build the user-item rating matrix.
        
        Args:
            ratings_data: List of (user_id, course_id, rating) tuples
            user_ids: Sorted list of all user IDs
            course_ids: Sorted list of all course IDs
        """
        self.user_ids = list(user_ids)
        self.course_ids = list(course_ids)

        user_idx_map = {uid: idx for idx, uid in enumerate(self.user_ids)}
        course_idx_map = {cid: idx for idx, cid in enumerate(self.course_ids)}

        n_users = len(self.user_ids)
        n_courses = len(self.course_ids)

        # Initialize with zeros (0 = unrated)
        self.user_item_matrix = np.zeros((n_users, n_courses))

        for user_id, course_id, rating in ratings_data:
            if user_id in user_idx_map and course_id in course_idx_map:
                u_idx = user_idx_map[user_id]
                c_idx = course_idx_map[course_id]
                self.user_item_matrix[u_idx, c_idx] = rating

        # Compute per-user mean ratings (ignoring zeros / unrated)
        self.user_means = np.zeros(n_users)
        for i in range(n_users):
            rated_mask = self.user_item_matrix[i] > 0
            if rated_mask.any():
                self.user_means[i] = self.user_item_matrix[i, rated_mask].mean()
            else:
                self.user_means[i] = 2.5  # default

    def fit(self):
        """
        Fit the KNN model on the user-item matrix.
        
        Uses cosine similarity as the distance metric, which captures
        rating pattern similarity regardless of scale differences.
        """
        if self.user_item_matrix is None:
            raise ValueError("Must call build_matrix() before fit()")

        # Clamp n_neighbors to available users
        k = min(self.n_neighbors, len(self.user_ids) - 1)
        self.knn_model = NearestNeighbors(
            n_neighbors=k,
            metric="cosine",
            algorithm="brute",
        )
        self.knn_model.fit(self.user_item_matrix)

    def predict_for_user(self, user_id):
        """
        Predict ratings for all unseen courses for a given user.
        
        Algorithm:
          1. Find K nearest neighbors (most similar users)
          2. For each unrated course, compute predicted rating as:
             pred = user_mean + weighted_sum(neighbor_deviations) / sum(weights)
          
          Where:
            - weight = 1 - cosine_distance (i.e., cosine similarity)
            - deviation = neighbor's rating - neighbor's mean rating
        
        Args:
            user_id: The target user's database ID
            
        Returns:
            Dict mapping course_id -> predicted_rating for unrated courses
        """
        if user_id not in self.user_ids:
            return {}

        u_idx = self.user_ids.index(user_id)
        user_vector = self.user_item_matrix[u_idx].reshape(1, -1)

        # Find K nearest neighbors
        distances, indices = self.knn_model.kneighbors(user_vector)
        # Convert cosine distances to similarities (1 - distance)
        similarities = 1 - distances.flatten()
        neighbor_indices = indices.flatten()

        predictions = {}

        for c_idx in range(len(self.course_ids)):
            # Skip already-rated courses
            if self.user_item_matrix[u_idx, c_idx] > 0:
                continue

            numerator = 0.0
            denominator = 0.0

            for n_pos, n_idx in enumerate(neighbor_indices):
                sim = similarities[n_pos]
                if sim <= 0:
                    continue  # Ignore negatively correlated users

                neighbor_rating = self.user_item_matrix[n_idx, c_idx]
                if neighbor_rating > 0:  # Only use neighbors who rated this course
                    # Mean-centered rating (deviation from neighbor's average)
                    deviation = neighbor_rating - self.user_means[n_idx]
                    numerator += sim * deviation
                    denominator += abs(sim)

            if denominator > 0:
                pred = self.user_means[u_idx] + (numerator / denominator)
                # Clamp to valid rating range
                predictions[self.course_ids[c_idx]] = max(1.0, min(5.0, pred))

        return predictions

    def get_top_n(self, user_id, n=5):
        """
        Get top-N course recommendations for a user.
        
        Returns:
            List of (course_id, predicted_rating) sorted by predicted rating desc
        """
        predictions = self.predict_for_user(user_id)
        sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        return sorted_preds[:n]
