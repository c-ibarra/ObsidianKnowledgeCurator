---
name: getContextSize
description: Calculates and displays the current conversation context window size, estimated token count, character count, and percentage of the model limit used.
argument-hint: 
---

# Antigravity Skill: getContextSize

When invoked via `/getContextSize`, calculate and display the current context window usage for the active Antigravity session.

## Process

1. **Measure Context Usage:**
   Execute a fast local Python inspection on the active Antigravity conversation transcript log:
   ```bash
   uv run python scripts/knowledge_commands.py --tokens
   ```

2. **Present Output:**
   Display the status box directly in the chat window.
