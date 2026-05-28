# Escalation Policy

The current AI is the supervisor. Pi is the worker.

## Immediate escalation

Take over immediately when:

- Pi encounters a permission error
- Pi cannot access the workspace correctly
- Pi is clearly acting on the wrong target
- Pi output conflicts with local facts

## Retry escalation

Track repeated failures by issue type, not by total call count.

Escalate when the same issue has failed 5 times.

Examples:

- the same broken command keeps failing
- the same auth/provider issue keeps recurring
- the same code path keeps being patched without fixing the bug

## Intervention steps

When escalating:

1. explain the blocker to yourself in one sentence
2. summarize what Pi already attempted
3. inspect local truth
4. choose one path:
   - fix environment
   - change Pi prompt
   - switch session
   - solve directly and then resume Pi
5. if Pi resumes, give a fresh, narrow instruction

## Never do this

- do not let Pi retry blindly forever
- do not trust Pi's success message without checking
- do not reset sessions casually just because a step failed
