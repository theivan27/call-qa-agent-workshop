# Lab 6: Evaluate before you ship

A demo that works once isn't a production agent. Test it the same way every time you change
the instructions, knowledge or tools.

## 1. Run the test cases
```bash
python scripts/evaluate.py
```
Each case in `evals/test_cases.json` starts a new conversation, then checks which tools were
called and what the reply contains. The cases check that the agent:
- Catches the missing disclosure and late verification in C-5532
- Catches the threats and the personal e-wallet in C-5533
- Suggests empathy coaching for C-5535
- Refuses to make HR decisions
- Never shows a full card number

Model output varies, so run it a few times. A case that fails now and then shows you where the
instructions are unclear.

## 2. Break something on purpose
Delete the **Boundaries** section from `api/qa_agent/instructions.md`, run
`python scripts/create_agent.py`, and run the evaluation again. Then put it back and recreate the agent.

## 3. Look at traces
In the Foundry portal, open your agent and review its traces and monitoring to see each run's
steps, tool calls, latency and token use. (Tracing needs an Application Insights resource
connected to your project.)

## Discuss
- What would you measure in production? For example: agreement with human QA scores, compliance
  breaches caught, time to feedback for agents, and cost per review.
- Which actions should always need a person's approval?

You're done!
