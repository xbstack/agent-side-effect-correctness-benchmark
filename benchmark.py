#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any


def state_matches(expected: Any, actual: Any) -> bool:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False
        return all(key in actual and state_matches(value, actual[key]) for key, value in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(expected) == len(actual) and all(
            state_matches(e, a) for e, a in zip(expected, actual)
        )
    return expected == actual


def effect_count(effects, needle):
    count = 0
    for effect in effects:
        if effect.get("type") != needle.get("type"):
            continue
        if needle.get("key") is not None and effect.get("key") != needle.get("key"):
            continue
        count += max(0, int(effect.get("count", 1)))
    return count


def effect_id(effect):
    return f"{effect.get('type')}:{effect.get('key')}" if effect.get("key") else str(effect.get("type"))


def evaluate(payload):
    trials = payload.get("trials") or []
    if not trials:
        raise ValueError("trials must contain at least one run")
    if "expected_terminal_state" not in payload:
        raise ValueError("expected_terminal_state is required")

    required = payload.get("expected_effects") or []
    forbidden = payload.get("forbidden_effects") or []
    evaluations = []

    for index, trial in enumerate(trials, start=1):
        if "terminal_state" not in trial:
            raise ValueError(f"trial {index} is missing terminal_state")
        effects = trial.get("effects") or []
        state_passed = state_matches(payload["expected_terminal_state"], trial["terminal_state"])
        missing, duplicate = [], []
        for expected in required:
            wanted = max(0, int(expected.get("count", 1)))
            actual = effect_count(effects, expected)
            if actual < wanted:
                missing.append(f"{effect_id(expected)} expected={wanted} actual={actual}")
            if actual > wanted:
                duplicate.append(f"{effect_id(expected)} expected={wanted} actual={actual}")

        forbidden_hits = []
        for item in forbidden:
            actual = effect_count(effects, item)
            if actual > 0:
                forbidden_hits.append(f"{effect_id(item)} actual={actual}")

        passed = state_passed and not missing and not duplicate and not forbidden_hits
        evaluations.append({
            "trial_id": trial.get("trial_id", str(index)),
            "passed": passed,
            "state_passed": state_passed,
            "required_effects_passed": not missing and not duplicate,
            "forbidden_effects_passed": not forbidden_hits,
            "false_success": bool(trial.get("claims_success")) and not passed,
            "missing_effects": missing,
            "duplicate_effects": duplicate,
            "forbidden_effects": forbidden_hits,
        })

    total = len(evaluations)
    passed = sum(1 for item in evaluations if item["passed"])
    false_success = sum(1 for item in evaluations if item["false_success"])
    return {
        "task_id": payload.get("task_id", "untitled-task"),
        "total_trials": total,
        "passed_trials": passed,
        "pass_rate": round(passed / total * 100, 1),
        "false_success_trials": false_success,
        "false_success_rate": round(false_success / total * 100, 1),
        "state_mismatch_trials": sum(1 for item in evaluations if not item["state_passed"]),
        "missing_effect_trials": sum(1 for item in evaluations if item["missing_effects"]),
        "duplicate_effect_trials": sum(1 for item in evaluations if item["duplicate_effects"]),
        "forbidden_effect_trials": sum(1 for item in evaluations if item["forbidden_effects"]),
        "evaluations": evaluations,
    }


def main():
    parser = argparse.ArgumentParser(description="Grade agent runs by terminal state and real side effects.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text())
    result = evaluate(payload)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
