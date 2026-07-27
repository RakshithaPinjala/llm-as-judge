from typing import Tuple
from .models import TestCase, JudgeVerdict, TestCaseResult
from .llm_client import LLMClient

JUDGE_PROMPT_TEMPLATE = """You are an impartial and expert judge evaluating the quality of two AI models.
You will be given a user input, an optional system prompt, and the outputs from Model A and Model B.
Your task is to evaluate which model provides a better response according to the provided criteria.

[User Input]:
{input}

[System Prompt]:
{system_prompt}

[Model A Output]:
{model_a_output}

[Model B Output]:
{model_b_output}

Instructions:
1. Evaluate each model on Correctness, Faithfulness, Completeness, Instruction-Following, Tone, and Safety.
2. For each criterion, provide a step-by-step reasoning BEFORE assigning a score from 1-5.
3. Provide an overall reasoning comparing both models. Penalize unhelpful verbosity, fluff, or sycophancy. Do not be fooled by polite but incorrect answers.
4. Finally, declare a winner ("model_a", "model_b", or "tie").
"""

class PairwiseJudge:
    def __init__(self, client: LLMClient):
        self.client = client
        
    def evaluate(self, test_case: TestCase) -> TestCaseResult:
        # A first, B second
        prompt_a_first = JUDGE_PROMPT_TEMPLATE.format(
            input=test_case.input,
            system_prompt=test_case.system_prompt or "None",
            model_a_output=test_case.model_a_output,
            model_b_output=test_case.model_b_output
        )
        
        # B first, A second
        prompt_b_first = JUDGE_PROMPT_TEMPLATE.format(
            input=test_case.input,
            system_prompt=test_case.system_prompt or "None",
            model_a_output=test_case.model_b_output,
            model_b_output=test_case.model_a_output
        )
        
        verdict_a_first, tokens_a = self.client.generate_structured(prompt_a_first, JudgeVerdict)
        verdict_b_first_raw, tokens_b = self.client.generate_structured(prompt_b_first, JudgeVerdict)
        
        # In the b_first scenario, "model_a" in the verdict actually refers to the original Model B
        mapped_winner_b_first = verdict_b_first_raw.winner
        if mapped_winner_b_first == "model_a":
            mapped_winner_b_first = "model_b"
        elif mapped_winner_b_first == "model_b":
            mapped_winner_b_first = "model_a"
            
        verdict_b_first_raw.winner = mapped_winner_b_first
        
        consistent_winner = None
        position_bias_flip = False
        
        if verdict_a_first.winner == verdict_b_first_raw.winner:
            consistent_winner = verdict_a_first.winner
        else:
            position_bias_flip = True
            
        return TestCaseResult(
            test_case_id=test_case.id,
            verdict_a_first=verdict_a_first,
            verdict_b_first=verdict_b_first_raw,
            consistent_winner=consistent_winner,
            position_bias_flip=position_bias_flip,
            tokens_used=tokens_a + tokens_b
        )
