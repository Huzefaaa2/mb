"""
Services Module - Core business logic and utilities for Magic Bus Compass 360
"""

from .gamification import (
    check_and_award_badges,
    get_user_badges,
    get_user_streak,
    get_motivational_message,
    update_streak,
    calculate_retention_impact,
    trigger_churn_intervention,
    predict_churn_risk,
)
from .peer_matching import (
    find_peer_mentors,
    calculate_similarity,
    match_peers,
)
from .skill_gap_bridger import (
    analyze_skill_gaps,
    generate_learning_paths,
    recommend_courses,
)

__all__ = [
    "check_and_award_badges",
    "get_user_badges",
    "get_user_streak",
    "get_motivational_message",
    "update_streak",
    "calculate_retention_impact",
    "trigger_churn_intervention",
    "predict_churn_risk",
    "find_peer_mentors",
    "calculate_similarity",
    "match_peers",
    "analyze_skill_gaps",
    "generate_learning_paths",
    "recommend_courses",
]
