# Lab 1: Your first agent

A **prompt agent** is a model plus instructions (and, later, tools) that Foundry hosts for you.

## 1. Read the instructions
Open `api/qa_agent/instructions.md`. It defines the agent's job, the review steps, how to handle
Taglish, the **boundaries** (no HR decisions, never reveal full numbers) and the report format.

## 2. Create the agent
```bash
python scripts/create_agent.py --stage 1
```
You should see `Agent ready: name=call-qa-reviewer version=1 stage=1 tools=0`.

## 3. Try it in the Foundry portal
1. In the Foundry portal, open **Agents**, select `call-qa-reviewer`, and open it in the playground.
2. Paste this transcript and ask: *"Review this call."*

```
Agent: Hi, is this Mr. Ramon Castillo?
Customer: Yes, speaking.
Agent: I'm calling because your personal loan account ending 2290 is 45 days past due with an outstanding balance of 38,500 pesos.
Customer: Wait, who is this?
Agent: Sorry, this is Liza from Northwind Bank collections. Can you confirm your birthday for me?
Customer: June 2, 1985. I thought I set up auto-debit already.
Agent: I see the auto-debit failed because of insufficient funds. Would you be able to pay the past-due amount this week, or would a payment plan help?
Customer: I can pay half on Friday and the rest next Friday.
Agent: That works. Please pay through the Northwind app or any branch. Your reference number is PA-20261001-122. Thank you, Mr. Castillo.
```

## What to notice
The agent gives a reasonable review, but it has **no scorecard or checklist yet**, so its scores
are generic and it can't cite rule numbers. Lab 2 fixes that.

**Next:** [Lab 2: Add knowledge](02-knowledge.md)
