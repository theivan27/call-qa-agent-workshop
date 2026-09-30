# Lab 3: Add tools

Give the agent **hands**: functions it can call to read calls and save results.

## 1. How function calling works
1. The agent's definition lists each tool's name, description and JSON parameters (`TOOL_SPECS` in `api/qa_agent/tools.py`).
2. When the agent wants a tool, Foundry returns a `function_call` item instead of a final answer.
3. **Your code** runs the function and sends back a `function_call_output`.
4. The agent continues until it has a final answer.

Steps 2 to 4 are the loop in `run_turn()` in `api/qa_agent/runner.py`. It's about 40 lines; read it.

## 2. Create the full agent
```bash
python scripts/create_agent.py --stage 3
```

## 3. Chat from your terminal
The Foundry playground doesn't run your functions (they live in your code), so use the CLI:
```bash
python scripts/chat_cli.py
```
Try these, one at a time:
1. `Review call C-5531 and log the QA score.`
2. `Check call C-5533 against the compliance checklist and flag every breach.`
3. `Review all collections calls and give me the top coaching themes.`
4. `Mark agent AG-103 as failed and notify HR.`

The CLI prints every tool call, so you can watch the agent plan its work.

## Guardrails to notice
- **Masking in code:** in C-5531 the customer reads out a full card number. `get_transcript` masks
  it before the model ever sees it (`_mask()` in `tools.py`).
- **Validation:** ask the agent to *"log a score of 110 for C-5534"*. `log_qa_score` rejects it and
  the agent has to correct itself.
- **Boundaries:** prompt 4 is refused by the instructions, and there is no HR tool to call anyway.

## Try this
Add a sixth tool, for example `get_agent_history(agent_id)` that returns past QA scores from
`QA_SCORES`. Add it to `IMPLEMENTATIONS` and `TOOL_SPECS`, rerun `create_agent.py`, and ask
*"How has AG-103 been scoring?"*

**Next:** [Lab 4: Run the web app](04-web-app.md)
