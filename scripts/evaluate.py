"""Run the test cases in evals/test_cases.json and report pass or fail for each.

Each case starts a fresh conversation, sends its prompts, then checks:
  expect_tools       tools that must be called
  forbid_tools       tools that must not be called
  reply_includes_any at least one of these phrases must appear in the final reply
  reply_must_not_match  a regular expression that must not match the reply (for example, full numbers)
"""
import json
import re
import sys

from _setup import ROOT
from qa_agent.runner import new_conversation, run_turn


def check(case: dict) -> list:
    conversation = new_conversation()
    called, reply = set(), ""
    for prompt in case["prompts"]:
        result = run_turn(conversation, prompt)
        called |= {step["name"] for step in result["trace"]}
        reply = result["reply"]

    problems = []
    for tool in case.get("expect_tools", []):
        if tool not in called:
            problems.append(f"expected tool {tool} was not called")
    for tool in case.get("forbid_tools", []):
        if tool in called:
            problems.append(f"forbidden tool {tool} was called")
    phrases = case.get("reply_includes_any")
    if phrases and not any(p.lower() in reply.lower() for p in phrases):
        problems.append(f"reply mentions none of {phrases}")
    pattern = case.get("reply_must_not_match")
    if pattern and re.search(pattern, reply):
        problems.append(f"reply matches forbidden pattern {pattern}")
    return problems


def main() -> None:
    cases = json.loads((ROOT / "evals" / "test_cases.json").read_text(encoding="utf-8"))
    failures = 0
    for case in cases:
        problems = check(case)
        status = "PASS" if not problems else "FAIL"
        failures += bool(problems)
        print(f"{status}  {case['name']}")
        for p in problems:
            print(f"      - {p}")
    print(f"\n{len(cases) - failures}/{len(cases)} passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
