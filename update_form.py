import re

with open(r"C:\Users\mohanpvr\.gemini\antigravity-ide\brain\e3042c9e-6469-4e49-84f8-cbad8e3862cf\form_answers.md", "r", encoding="utf-8") as f:
    content = f.read()

new_diagram = """```mermaid
graph TD
    classDef file fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b
    classDef logic fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef output fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef mitigate fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#f57f17
    
    A[Test Suite Input<br/>JSON/YAML]:::file
    B[Config<br/>YAML]:::file
    C[LLM Judge Model API<br/>OpenAI/Gemini]:::logic
    
    A --> D
    B --> D
    C --> D
    
    subgraph Evaluator Orchestrator
        D[Parse Test Cases<br/>Pydantic Models]:::logic
        E[Judging-Prompt Construction]:::logic
        
        M1[BIAS MITIGATION:<br/>A/B Position Order Swap<br/>Construct Prompt A->B and B->A]:::mitigate
        E --> M1
        
        M1 --> F[Judge Model API Call]:::logic
        
        F --> G[Structured-Verdict Parsing<br/>with Malformed-JSON Fallback / Retry]:::logic
        G --> H[Per-Case Aggregation]:::logic
    end
    
    H --> I[Suite Report Generation]:::logic
    I --> J[Metrics<br/>JSON Logs]:::output
```"""

# Update mermaid diagram
content = re.sub(r'```mermaid.*?```', new_diagram, content, flags=re.DOTALL)

# Add new sections before 2.3
new_sections = """
### 2.1 Problem 2 - Architecture Diagram / Flowchart (Google Drive Link)
> [!IMPORTANT]
> **Action Required**: Take a screenshot of the detailed Mermaid architecture diagram located in the README.md file (or rendered on GitHub), upload it to Google Drive, ensure it is set to "Anyone with the link", and paste the link here.

### Problem 2 — Prerequisites
```text
Runtime + Version: Python 3.10+
OS: Windows, macOS, or Linux (cross-platform)
Services: Valid API key for OpenAI or Gemini (Google GenAI)
Hardware assumptions: Standard development laptop (no local GPU required, inference via API)
```

### Problem 2 — Environment variables
```text
OPENAI_API_KEY
GEMINI_API_KEY
```

### Problem 2 — Install & 2.2 Setup & Run Instructions
*(You can paste this exact snippet for both the "Install" and "Setup & Run" sections)*
```bash
# Clone the repository
git clone https://github.com/RakshithaPinjala/llm-as-judge.git
cd llm-as-judge

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (fill in keys)
copy .env.example .env

# Run the standard evaluation suite
python eval/run_eval.py

# Run the adversarial judge validation suite
python eval/validate_judge.py
```

---

"""

if "2.1 Problem 2" not in content:
    content = content.replace("### Problem 2 — 2.3 Evaluation Results", new_sections + "### Problem 2 — 2.3 Evaluation Results")

# Add new sections to Reflections
reflections_additions = """
**Problem 2 — 2.4.1 Judging Mode Rationale**
> We chose Pairwise A-vs-B comparison. While pointwise scoring suffers from absolute score clustering (where judges tend to lazily give 4s or 5s to everything), pairwise forces the judge to make a relative choice, providing a much stronger and clearer signal for A/B testing two prompts or models. The primary trade-off is cost (since position bias requires evaluating both A->B and B->A permutations).

**Problem 2 — 2.4.2 Structured Verdict Parsing & Recovery**
> We enforce structured verdicts by explicitly passing a strict Pydantic JSON schema to the LLM judge. The raw text response is then parsed back into these Pydantic models. To handle and recover from malformed JSON (or hallucinated extra text), we wrap the generation call with the `tenacity` library, which automatically triggers an exponential backoff and retry loop until a valid, schema-compliant JSON is returned.

"""

if "2.4.1 Judging Mode Rationale" not in content:
    content = content.replace("**Problem 2 — 2.4.3 Judge Model", reflections_additions + "**Problem 2 — 2.4.3 Judge Model")

with open(r"C:\Users\mohanpvr\.gemini\antigravity-ide\brain\e3042c9e-6469-4e49-84f8-cbad8e3862cf\form_answers.md", "w", encoding="utf-8") as f:
    f.write(content)

# Update README diagram as well
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()
readme = re.sub(r'```mermaid.*?```', new_diagram, readme, flags=re.DOTALL)
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
