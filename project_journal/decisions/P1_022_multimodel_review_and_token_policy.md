# P1-022 Multimodel Review And Token Policy

Date: 2026-05-23

## Decision

Do not connect Claude API now.

Use Claude Web or Claude App manually for the first Reviewer checks. Consider a future `P2_claude_reviewer_api_module` only after 3-5 manual review cycles are stable.

## Roles

- Codex = Builder.
- Claude = Reviewer.
- User = Owner.

AI cannot self-approve.

## Current Review Flow

```text
Codex builds -> Codex produces Review Package -> Claude reviews manually -> User decides
```

## Claude API Rule

Claude API is deferred.

API integration may be reconsidered only after:

- At least 3-5 manual review cycles are completed.
- Review Package format is stable.
- Reviewer outputs are useful and compact.
- The business MVP is not blocked by manual review.

## Current Business MVP Completion Conditions

The current MVP is considered business-ready when:

1. `dog_bath_hose` product-level pipeline runs end to end.
2. Voiceover-only render policy runs successfully.
3. Experiment racing templates start recording real data.
4. `P1_021` firewall review passes and is committed.

## Codex Report Compression Rule

Future Codex reports should be compressed to:

1. Task name.
2. Modified files.
3. New files.
4. Boundary status.
5. Test status.
6. Key risks.
7. Review Package summary.
8. Next recommendation.

Avoid long narrative unless the task is high-risk or the user explicitly asks for detail.

## Claude Review Compression Rule

Claude review output should be compressed to:

1. `pass` / `pass_with_warnings` / `fail`.
2. Must-fix items.
3. Optional improvements.
4. Whether commit is allowed.

## User Decision States

User final decisions should be one of:

- `commit`
- `patch`
- `rollback`

## Token Control Principle

The current goal is business MVP progress, not a complete multi-model automation system.

Use manual review and compact reporting until automation saves more time than it costs.

## Not In Scope Now

- No Claude API connection.
- No external API calls.
- No dependency installation.
- No business code changes.
- No video generation.
- No ffmpeg execution.
- No GitHub push handling.
