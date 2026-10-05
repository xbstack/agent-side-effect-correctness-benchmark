# XBSTACK Agent Side-Effect Correctness Benchmark

A small deterministic harness for grading tool-using agents by **terminal backend state and real side effects** rather than by final-answer fluency.

## Why this exists

Microsoft / Hugging Face ThinkingBox makes the core reliability problem concrete: a tool-using agent can produce a convincing transcript while leaving the backend in the wrong state. ThinkingBox-Bench v1.0 contains 507 stateful business-workflow tasks and primarily uses executable checks over terminal backend state and side effects, then repeats each task to study reliability.

This XBSTACK harness is **independent**. It does not copy or run ThinkingBox-Bench tasks, golden states, trajectories, or grading code. It applies the same broad engineering principle to XBSTACK-style production checks and user-supplied fixtures.

## What is graded

Each task defines:

- `expected_terminal_state`: a subset of backend state that must match;
- `expected_effects`: effects that must occur exactly the expected number of times;
- `forbidden_effects`: effects that must not happen;
- `trials`: repeated runs with actual terminal state and effects;
- `claims_success`: whether the agent told the user the task succeeded.

The report includes:

- trial pass rate;
- false-success rate;
- terminal-state mismatches;
- missing effects;
- duplicate effects;
- forbidden effects;
- literal observed all-pass task count;
- per-trial evidence.

## Run one task

The original single-task format remains supported:

```bash
python3 benchmark.py fixtures/refund-order.json \
  --output results/refund-order-results.json
```

## Run the synthetic suite

```bash
python3 benchmark.py examples/synthetic-suite.json
```

The current suite contains 4 original XBSTACK synthetic tasks and 12 recorded trials covering:

1. refund false success;
2. duplicate payment after retry/resume;
3. forbidden notification leakage;
4. publish-state mismatch.

They are synthetic regression fixtures, not model benchmark results and not ThinkingBox-Bench tasks.

Current deterministic fixture result:

```text
tasks=4
trials=12
passed=5
pass_rate=41.7%
false_success_rate=50.0%
state_mismatch_trials=4
duplicate_effect_trials=2
missing_effect_trials=3
forbidden_effect_trials=1
observed_all_pass_tasks=0/4
```

These numbers describe the deliberately mixed pass/fail fixture shipped in this repository. They do **not** describe any model's real-world performance.

## CI release gate

```bash
python3 benchmark.py examples/synthetic-suite.json --fail-on-any-error
```

The command exits non-zero when any supplied trial fails.

## Metric interpretation

- **Pass rate**: share of supplied trials that satisfy terminal-state, required-effect, and forbidden-effect checks.
- **False success**: `claims_success=true` while deterministic outcome checks fail.
- **State mismatch**: the actual backend state does not contain the required expected state.
- **Missing effect**: a required effect occurs fewer times than expected.
- **Duplicate effect**: a required effect occurs more times than expected.
- **Forbidden effect**: an explicitly prohibited effect occurs.
- **Observed all-pass tasks**: literal count of tasks whose supplied trials all pass. It is not a statistical pass@k estimator.

## Online evaluator

Use the browser-local XBSTACK evaluator with your own terminal-state and side-effect records:

https://www.xbstack.com/en/tools/agent-side-effect-evaluator/?utm_source=github&utm_medium=referral&utm_campaign=agent_side_effect_correctness&utm_content=repo_readme&ref=github

Chinese:

https://www.xbstack.com/tools/agent-side-effect-evaluator/?utm_source=github&utm_medium=referral&utm_campaign=agent_side_effect_correctness&utm_content=repo_readme_zh&ref=github

## Important boundary

This is not an LLM leaderboard and not a security certification. Production evaluation still needs representative tasks, isolated state, controlled tools, versioned fixtures, and repeated trials.

Use deterministic state/effect checks when the requirement can be represented that way. Use a narrow semantic judge only for requirements that cannot be reduced to backend state or observable effects.

## References

- Microsoft / Hugging Face ThinkingBox: https://huggingface.co/blog/microsoft/thinkingbox
- Microsoft ThinkingBox: https://github.com/microsoft/thinkingbox
- ThinkingBox data: https://github.com/microsoft/thinkingbox-data
- ThinkingBox-Bench dataset: https://huggingface.co/datasets/microsoft/ThinkingBox-Bench

## License

MIT.
