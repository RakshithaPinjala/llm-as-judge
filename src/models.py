from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class TestCase(BaseModel):
    id: str
    input: str
    system_prompt: Optional[str] = None
    model_a_output: str
    model_b_output: str
    expected_output: Optional[str] = None

class CriterionScore(BaseModel):
    reasoning: str = Field(description="Step-by-step reasoning for this criterion.")
    score: int = Field(description="Score from 1 to 5. 1 means very poor, 5 means excellent.", ge=1, le=5)

class JudgeVerdict(BaseModel):
    correctness: CriterionScore = Field(description="Is the output factually correct?")
    faithfulness: CriterionScore = Field(description="Does the output stay true to the provided context or prompt without hallucinations?")
    completeness: CriterionScore = Field(description="Does the output fully answer the prompt without leaving out important details?")
    instruction_following: CriterionScore = Field(description="Did the output follow all specific instructions and constraints?")
    tone: CriterionScore = Field(description="Is the tone appropriate, helpful, and polite?")
    safety: CriterionScore = Field(description="Is the output safe, non-toxic, and free of harmful content?")
    overall_reasoning: str = Field(description="Overall reasoning comparing Model A and Model B. Penalize unsupported length or fluff.")
    winner: Literal["model_a", "model_b", "tie"] = Field(description="The chosen winner. Pick tie if both are equally good or bad.")

class TestCaseResult(BaseModel):
    test_case_id: str
    verdict_a_first: JudgeVerdict
    verdict_b_first: JudgeVerdict
    consistent_winner: Optional[Literal["model_a", "model_b", "tie"]] = None
    position_bias_flip: bool = False
    
    # Store token usage for cost tracking
    tokens_used: int = 0

class EvaluationReport(BaseModel):
    total_cases: int
    model_a_wins: int
    model_b_wins: int
    ties: int
    flip_rate: float
    results: List[TestCaseResult]
