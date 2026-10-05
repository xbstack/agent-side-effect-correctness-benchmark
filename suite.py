#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from benchmark import evaluate


def evaluate_suite(payload):
    tasks = payload.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks must contain at least one task")

    task_reports = [evaluate(task) for task in tasks]
    total_trials = sum(item["total_trials"] for item in task_reports)
    passed_trials = sum(item["passed_trials"] for item in task_reports)
    false_success_trials = sum(item["false_success_trials"] for item in task_reports)

    summary = {
        "tasks": len(task_reports),
        "trials": total_trials,
        "passed": passed_trials,
        "pass_rate": round(passed_trials / total_trials * 100, 1),
        "false_success_trials": false_success_trials,
        "false_success_rate": round(false_success_trials / total_trials * 100, 1),
        "state_mismatch_trials": sum(item["state_mismatch_trials"] for item in task_reports),
        "duplicate_effect_trials": sum(item["duplicate_effect_trials"] for item in task_reports),
        "missing_effect_trials": sum(item["missing_effect_trials"] for item in task_reports),
        "forbidden_effect_trials": sum(item["forbidden_effect_trials"] for item in task_reports),
        "observed_all_pass_tasks": sum(item["passed_trials"] == item["total_trials"] for item in task_reports),
        "task_count": len(task_reports),
    }

    return {"summary": summary, "tasks": task_reports}


def main():
    parser = argparse.ArgumentParser(description="Aggregate terminal-state and side-effect checks across multiple agent tasks.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on-any-error", action="store_true")
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    report = evaluate_suite(payload)
    summary = report["summary"]

    print(f"tasks={summary['tasks']}")
    print(f"trials={summary['trials']}")
    print(f"passed={summary['passed']}")
    print(f"pass_rate={summary['pass_rate']}%")
    print(f"false_success_rate={summary['false_success_rate']}%")
    print(f"state_mismatch_trials={summary['state_mismatch_trials']}")
    print(f"duplicate_effect_trials={summary['duplicate_effect_trials']}")
    print(f"missing_effect_trials={summary['missing_effect_trials']}")
    print(f"forbidden_effect_trials={summary['forbidden_effect_trials']}")
    print(f"observed_all_pass_tasks={summary['observed_all_pass_tasks']}/{summary['task_count']}")

    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")

    if args.fail_on_any_error and summary["passed"] != summary["trials"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
