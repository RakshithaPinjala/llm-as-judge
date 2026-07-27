import json
from typing import List, Dict, Any
from tqdm import tqdm
from .models import TestCase, EvaluationReport, TestCaseResult
from .judge import PairwiseJudge

class Evaluator:
    def __init__(self, judge: PairwiseJudge):
        self.judge = judge
        
    def evaluate_suite(self, test_suite: List[TestCase]) -> EvaluationReport:
        results = []
        model_a_wins = 0
        model_b_wins = 0
        ties = 0
        flips = 0
        
        for case in tqdm(test_suite, desc="Evaluating Test Cases"):
            try:
                result = self.judge.evaluate(case)
                results.append(result)
                
                if result.position_bias_flip:
                    flips += 1
                elif result.consistent_winner == "model_a":
                    model_a_wins += 1
                elif result.consistent_winner == "model_b":
                    model_b_wins += 1
                else:
                    ties += 1
                    
            except Exception as e:
                print(f"Error evaluating test case {case.id}: {e}")
                
        total_cases = len(test_suite)
        flip_rate = flips / total_cases if total_cases > 0 else 0.0
        
        return EvaluationReport(
            total_cases=total_cases,
            model_a_wins=model_a_wins,
            model_b_wins=model_b_wins,
            ties=ties,
            flip_rate=flip_rate,
            results=results
        )
