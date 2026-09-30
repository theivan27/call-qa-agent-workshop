# Lab 2: Add knowledge

Ground the agent in your organization's own rules with the **file search** tool.

## 1. Look at the knowledge files
Open the three files in `knowledge/`: the QA scorecard (five criteria, 100 points), the compliance
checklist (CC-01 to CC-07) and the coaching guide.

## 2. Create a new version with knowledge
```bash
python scripts/create_agent.py --stage 2
```
The script uploads `knowledge/*.md` to a vector store named `call-qa-knowledge` and attaches it to
the agent with `FileSearchTool`. See `ensure_vector_store()` in `scripts/create_agent.py`.

## 3. Test it again
Refresh the playground and paste the same transcript. This time the agent should:
- Score each criterion using the scorecard's point values
- Flag **CC-01** (no recording disclosure) and **CC-02** (balance discussed before verification)

## Try this
Add a rule to `knowledge/compliance_checklist.md`, for example
`| CC-08 | Offer to send a written summary by SMS or email. | Low |`, then run:
```bash
python scripts/create_agent.py --stage 2 --refresh-knowledge
```
Ask the agent about CC-08. The policy changed without any code change.

**Next:** [Lab 3: Add tools](03-tools.md)
