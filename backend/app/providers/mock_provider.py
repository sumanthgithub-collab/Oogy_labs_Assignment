import logging
from typing import Dict, Any, Optional
from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class MockLLMProvider(LLMProvider):
    def __init__(self, model_name: str = "mock-lenny-v1"):
        self.model_name = model_name

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        prompt_lower = prompt.lower()

        # Handle explicit refusal prompt
        if "out-of-bounds" in prompt_lower or "out of domain" in prompt_lower:
            return "The Lenny Growth Assistant knowledge base is focused on product management, growth, strategy, and PLG. It does not contain information to answer this specific query."

        # Handle Ship 30 essay generation
        if "ship 30" in prompt_lower or "essay" in prompt_lower:
            return """# Tactical Product & Growth Framework

## Hook: Most Product Teams Are Doing It Wrong
If you treat every task on your roadmap with equal importance, you're paving the path to team burnout and diluted strategic impact. 

---

## 3 Actionable Takeaways

### 1. Categorize Every Task Before Executing
- **Leverage (L)**: High-impact strategic work where 10x effort yields 10x return.
- **Neutral (N)**: Standard operations where good enough is sufficient.
- **Overhead (O)**: Administrative tax to execute with minimal viable effort.

### 2. Guard Your Energy Windows
Focus your peak cognitive hours exclusively on Leverage items. Batch low-leverage Overhead tasks during low-energy slots.

### 3. Establish Clear Proxy Metrics
Don't rely on lagging metrics. Define immediate proxy indicators that correlate directly with long-term retention and customer delight.

---

## TL;DR & Action Step
**TL;DR**: High leverage comes from ruthless prioritization. Tag tomorrow's to-do list with L, N, or O, and dedicate 70% of your focused energy to your single biggest L-task.
"""

        # Handle HTML Artifact generation
        if "html" in prompt_lower or "visual artifact" in prompt_lower or "card" in prompt_lower:
            return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 24px; margin: 0; }
  .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 24px; max-width: 600px; margin: 0 auto; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
  .title { font-size: 20px; font-weight: 700; color: #ff6b00; margin-bottom: 12px; }
  .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 16px; }
  .box { background: #0f172a; padding: 16px; border-radius: 8px; text-align: center; border-left: 4px solid #ff6b00; }
  .label { font-size: 14px; font-weight: 600; color: #e2e8f0; }
  .sub { font-size: 12px; color: #94a3b8; margin-top: 4px; }
</style>
</head>
<body>
  <div class="card">
    <div class="title">🚀 Lenny Growth Summary Artifact</div>
    <p style="color: #cbd5e1; font-size: 14px;">Key tactical framework synthesized from Lenny's Podcast knowledge base.</p>
    <div class="grid">
      <div class="box">
        <div class="label">Leverage (L)</div>
        <div class="sub">10x Output Tasks</div>
      </div>
      <div class="box">
        <div class="label">Neutral (N)</div>
        <div class="sub">Standard Execution</div>
      </div>
      <div class="box">
        <div class="label">Overhead (O)</div>
        <div class="sub">Minimum Viable Tax</div>
      </div>
    </div>
  </div>
</body>
</html>"""

        # General grounded answer simulation
        return """Based on the insights from Lenny's Podcast:

High-leverage product leaders focus on compounding impact rather than brute-force task completion. 

Key principles cited:
- **LNO Framework**: Categorize tasks into Leverage, Neutral, and Overhead to allocate your time effectively.
- **Growth Loops over Funnels**: Replace linear acquisition funnels with self-reinforcing loops (acquisition, retention, monetization).
- **Product-Market-Channel Fit**: Ensure your product design aligns with your acquisition channels and monetization model.
"""

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "mock",
            "model_name": self.model_name,
            "status": "active"
        }
