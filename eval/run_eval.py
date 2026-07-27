import sys
import os
import yaml
import json
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
    
    try:
        client = get_client(provider, model_name)
    except Exception as e:
        print(f"Failed to initialize client: {e}")
        print("Make sure your .env file is set up with correct API keys.")
        sys.exit(1)
        
    judge = PairwiseJudge(client)
    evaluator = Evaluator(judge)
    
    suite_path = config.get("paths", {}).get("test_suite", "data/sample_suite.json")
    print(f"Loading test suite from {suite_path}")
    
    try:
        with open(suite_path, "r", encoding="utf-8") as f:
            raw_suite = json.load(f)
            test_suite = [TestCase(**case) for case in raw_suite]
    except Exception as e:
        print(f"Error loading test suite: {e}")
        sys.exit(1)
        
    print(f"Evaluating {len(test_suite)} cases...")
    report = evaluator.evaluate_suite(test_suite)
    
    out_dir = config.get("paths", {}).get("output_dir", "results")
    os.makedirs(out_dir, exist_ok=True)
    
    metrics_path = os.path.join(out_dir, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))
        
    print("\n" + "="*40)
    print("         EVALUATION REPORT")
    print("="*40)
    print(f"Total Cases Evaluated  : {report.total_cases}")
    print(f"Model A Consistent Wins: {report.model_a_wins}")
    print(f"Model B Consistent Wins: {report.model_b_wins}")
    print(f"Consistent Ties        : {report.ties}")
    print(f"Position Bias Flip Rate: {report.flip_rate:.2%} ({(report.flip_rate * report.total_cases):.0f} cases)")
    print("-"*40)
    
    if report.model_a_wins > report.model_b_wins:
        print("*** OVERALL WINNER: MODEL A ***")
    elif report.model_b_wins > report.model_a_wins:
        print("*** OVERALL WINNER: MODEL B ***")
    else:
        print("*** OVERALL WINNER: TIE ***")
        
    print(f"\nDetailed results saved to {metrics_path}")

if __name__ == "__main__":
    main()
