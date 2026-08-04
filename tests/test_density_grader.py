#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root and scripts directory to python path
PROJECT_DIR = Path(__file__).parent.parent
sys.path.append(str(PROJECT_DIR / "scripts"))

from density_grader import grade_technical_density

HIGH_DENSITY_SAMPLE = """
# Implementing a Custom Attention Layer in PyTorch

In this guide, we implement a custom Scaled Dot-Product Attention layer. The mathematical formulation is:
$$Attention(Q, K, V) = softmax(\\frac{QK^T}{\\sqrt{d_k}})V$$

Here is the implementation:
```python
import torch
import torch.nn as nn
import math

class ScaledDotProductAttention(nn.Module):
    def __init__(self, d_k):
        super().__init__()
        self.d_k = d_k
        self.softmax = nn.Softmax(dim=-1)
        
    def forward(self, q, k, v, mask=None):
        # q, k, v shapes: [batch_size, num_heads, seq_len, d_k]
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
            
        attn_weights = self.softmax(scores)
        output = torch.matmul(attn_weights, v)
        return output, attn_weights
```
This layer runs in $O(N^2)$ time where $N$ is the sequence length, and is the core building block of Multi-Head Attention mechanisms in Transformer architectures.
"""

LOW_DENSITY_SAMPLE = """
# What is Artificial Intelligence? A Quick Beginner Guide!

Hello friends! Today we are talking about AI! Artificial Intelligence is super cool!
AI is basically like a digital brain that lives inside computers. It can think, make decisions, and learn from its mistakes, just like a human!

Here is why AI is going to change the world:
- It makes searching the web faster.
- It writes emails for you.
- It can generate funny pictures of cats!

If you want to learn coding and make your own AI, you should sign up for our coding bootcamp! Use promo code AWESOME_AI for 20% off. Don't forget to like, subscribe, and share this article!
"""

def is_skipped_or_failed(res) -> bool:
    score = res.get("score")
    reason = res.get("reason", "")
    # If API/provider failed and defaulted, it returns score 1.0 with a fallback/failure message.
    if score == 1.0 and any(kw in reason.lower() for kw in ["not configured", "failed", "skipped", "timeout"]):
        print(f"\n[!] WARNING: Grader was skipped or failed due to configuration/connection issues.")
        print(f"    Grader Reason: {reason}")
        print("    Please configure a valid GEMINI_API_KEY in .env, or ensure Ollama is running.")
        return True
    return False

def test_high_density():
    print("Testing High Density Grader...")
    res = grade_technical_density(HIGH_DENSITY_SAMPLE)
    print(f"High Density Score: {res.get('score')} | Reason: {res.get('reason')}")
    if is_skipped_or_failed(res):
        print("test_high_density: SKIPPED (No valid API key or local LLM connection)")
        return
    assert res.get("score") >= 0.7, f"Expected high density score >= 0.7, got {res.get('score')}"
    print("test_high_density: PASS")

def test_low_density():
    print("Testing Low Density Grader...")
    res = grade_technical_density(LOW_DENSITY_SAMPLE)
    print(f"Low Density Score: {res.get('score')} | Reason: {res.get('reason')}")
    if is_skipped_or_failed(res):
        print("test_low_density: SKIPPED (No valid API key or local LLM connection)")
        return
    assert res.get("score") <= 0.4, f"Expected low density score <= 0.4, got {res.get('score')}"
    print("test_low_density: PASS")

def main():
    print("=== RUNNING TECHNICAL DENSITY GRADER TESTS ===")
    try:
        test_high_density()
        print("-" * 50)
        test_low_density()
        print("=== DENSITY TESTS COMPLETED ===")
    except AssertionError as e:
        print(f"=== TEST FAILED: {e} ===", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"=== ERROR RUNNING TESTS: {e} ===", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
