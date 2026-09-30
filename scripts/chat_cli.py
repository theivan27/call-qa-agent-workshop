"""Chat with the agent in your terminal. Shows every tool call the agent makes.

Commands: /new starts a new conversation, /quit exits.
"""
import json

from _setup import ROOT  # noqa: F401
from qa_agent.runner import new_conversation, run_turn


def show_trace(trace: list) -> None:
    for step in trace:
        if step["type"] == "file_search":
            print("  [knowledge] searched the QA knowledge files")
        else:
            args = json.dumps(step["arguments"], ensure_ascii=False)
            print(f"  [tool] {step['name']}({args[:160]}{'...' if len(args) > 160 else ''})")
            if isinstance(step["result"], dict) and "error" in step["result"]:
                print(f"         error: {step['result']['error']}")


def main() -> None:
    conversation = new_conversation()
    print("Call QA Reviewer. Try: Review call C-5531.  (/new, /quit)\n")
    while True:
        try:
            text = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        if text == "/quit":
            break
        if text == "/new":
            conversation = new_conversation()
            print("(new conversation)\n")
            continue
        result = run_turn(conversation, text)
        show_trace(result["trace"])
        print(f"\nagent> {result['reply']}\n")


if __name__ == "__main__":
    main()
