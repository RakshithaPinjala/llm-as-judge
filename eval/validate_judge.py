import sys
import os
import json
import yaml
from sklearn.metrics import cohen_kappa_score, accuracy_score
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm_client import get_client
from src.judge import PairwiseJudge
from src.evaluator import Evaluator
from src.models import TestCase

def main():
    load_dotenv()
    with open("configs/config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    provider = config.get("judge", {}).get("provider", "openai")
    model_name = config.get("judge", {}).get("model_name", "gpt-4o-mini")
    print(f"Initializing Judge Client: {provider} ({model_name})")
    client = get_client(provider, model_name)
    judge = PairwiseJudge(client)
    evaluator = Evaluator(judge)
    
    suite_path = "data/adversarial_suite.json"
    print(f"Loading adversarial suite from {suite_path}")
    with open(suite_path, "r", encoding="utf-8") as f:
        raw_suite = json.load(f)
        
    test_suite = [TestCase(**case) for case in raw_suite]
    expected_labels = [case.get("expected_output") for case in raw_suite]
    
    print(f"Running Judge Validation on {len(test_suite)} adversarial cases...")
    report = evaluator.evaluate_suite(test_suite)
    
    actual_labels = []
    for result in report.results:
        # If there's a position bias flip, we consider it a 'tie' for validation purposes
        actual_labels.append(result.consistent_winner if result.consistent_winner else "tie")
        
    y_true = []
    y_pred = []
    for expected, actual in zip(expected_labels, actual_labels):
        if expected:
            y_true.append(expected)
            y_pred.append(actual)
            
    if not y_true:
        print("No expected labels found for validation.")
        return
        
    acc = accuracy_score(y_true, y_pred)
    # Using specific labels to ensure kappa calculates correctly even if some classes are missing
    labels = ["model_a", "model_b", "tie"]
    kappa = cohen_kappa_score(y_true, y_pred, labels=labels)
    
    print("\n" + "="*40)
    print("      JUDGE VALIDATION REPORT")
    print("="*40)
    print(f"Agreement Rate (Accuracy): {acc:.2%}")
    print(f"Cohen's Kappa Score      : {kappa:.3f}")
    print(f"Position Bias Flip Rate  : {report.flip_rate:.2%}")
    
    print("\nDetailed Case Analysis:")
    for case, expected, actual in zip(raw_suite, expected_labels, actual_labels):
        bias_type = case.get("bias_type", "unknown")
        status = "[PASS]" if expected == actual else "[FAIL]"
        print(f"- {status} | Bias: {bias_type.upper():<10} | Expected: {expected:<7} | Judge Picked: {actual}")

if __name__ == "__main__":
    main()
