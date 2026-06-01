# ViraNova Influencer Scoring Engine (Ratefluencer Score™)

import numpy as np

class RatefluencerScoringEngine:
    def __init__(self):
        # In a real environment, this loads the XGBoost model: ratefluencer_xgb.pkl
        pass

    def calculate_score(self, authenticity: float, growth: float, engagement: float, brand_match: float) -> int:
        """
        Runs XGBoost prediction based on normalized features.
        """
        weights = [0.3, 0.25, 0.25, 0.2]
        features = np.array([authenticity, growth, engagement, brand_match])
        score = np.dot(features, weights)
        return int(np.clip(score, 0, 100))

scoring_engine = RatefluencerScoringEngine()
