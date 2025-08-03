import random
from typing import List, Dict, Any

class SmartMatchingAlgorithm:
    """
    Matches candidates to interviewers based on skills, experience, and availability.
    """
    def __init__(self, interviewer_profiles: List[Dict[str, Any]]):
        self.interviewer_profiles = interviewer_profiles

    def match(self, candidate_skills: Dict[str, int], candidate_experience: int, interviewer_availability: Dict[str, List[str]]) -> Dict[str, Any]:
        best_match = None
        best_score = 0
        for interviewer in self.interviewer_profiles:
            score = self._calculate_score(candidate_skills, candidate_experience, interviewer)
            available = interviewer_availability.get(interviewer['id'], [])
            if available:
                score += 10  # Bonus for availability
            if score > best_score:
                best_score = score
                best_match = interviewer
        if best_match:
            return {
                'interviewer': best_match,
                'confidence': round(best_score / 100, 2)
            }
        # Fallback: return random interviewer with low confidence
        fallback = random.choice(self.interviewer_profiles) if self.interviewer_profiles else None
        return {
            'interviewer': fallback,
            'confidence': 0.3
        }

    def _calculate_score(self, candidate_skills, candidate_experience, interviewer):
        score = 0
        for skill, level in candidate_skills.items():
            interviewer_level = interviewer.get('skills', {}).get(skill, 0)
            score += min(level, interviewer_level) * 5
        score += min(candidate_experience, interviewer.get('experience', 0)) * 2
        return score

def create_sample_interviewer_profiles() -> List[Dict[str, Any]]:
    """
    Returns a list of sample interviewer profiles for testing.
    """
    return [
        {
            'id': 'int1',
            'name': 'Alice',
            'skills': {'python': 5, 'sql': 4, 'ml': 3},
            'experience': 7
        },
        {
            'id': 'int2',
            'name': 'Bob',
            'skills': {'python': 3, 'sql': 5, 'ml': 2},
            'experience': 5
        },
        {
            'id': 'int3',
            'name': 'Carol',
            'skills': {'python': 4, 'sql': 3, 'ml': 5},
            'experience': 6
        }
    ]
