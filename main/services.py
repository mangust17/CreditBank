class CreditService:
    def __init__(self):
        self.scoring_system = ScoringSystem()

    def evaluate_application(self, data):
        return self.scoring_system.calculate_score(data)

class ScoringSystem:
    def calculate_score(self, data):
        return 75  