# XBSTACK Agent Side-Effect Correctness Benchmark

A small deterministic harness for grading tool-using agents by **terminal backend state and real side effects** rather than by final-answer fluency.

## Why this exists

Microsoft / Hugging Face ThinkingBox makes the core reliability problem concrete: a tool-using agent can produce a convincing transcript while leaving the backend in the wrong state. ThinkingBox-Bench evaluates 507 stateful business workflows primarily with executable checks over terminal state and side effects, and repeats tasks to study reliability.

This XBSTACK harness is **independent**. It does not copy or run ThinkingBox-Bench tasks. It applies the same broad engineering principle to XBSTACK-style production checks and user-supplied fixtures.

## What is graded

Each task defines:

- `expected_terminal_state`: a subset of backend state that must match.
- `expected_effects`: side effects that must occur exactly the expected number of times.
- `forbidden_effects`: effects that must not happen.
- `trials`: repeated agent runs with actual terminal state and effects.
- `claims_success`: whether the agent told the user the task succeeded.

The report includes:

- task pass rate;
- false-success rate;
- terminal-state mismatches;
- missing effects;
- duplicate effects;
- forbidden effects;
- per-trial evidence.

## Run

```bash
python3 benchmark.py fixtures/refund-order.json \
  --output results/refund-order-results.json
```

The included fixture deliberately has:

1. one correct run;
2. one false success where the agent says the refund completed but backend state is still pending;
3. one duplicate side effect where the refund happens twice.

## Important boundary

This is not an LLM benchmark leaderboard and not a security certification. It is a deterministic outcome checker. Production evaluation still needs representative tasks, isolated test state, controlled tools, versioned fixtures, and repeated trials.

## References

- Microsoft / Hugging Face ThinkingBox: https://huggingface.co/blog/microsoft/thinkingbox
- Microsoft ThinkingBox: https://github.com/microsoft/thinkingbox
- ThinkingBox data: https://github.com/microsoft/thinkingbox-data
