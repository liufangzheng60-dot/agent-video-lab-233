# AGENTS.md

Permanent operating contract for Codex on this repository.

## Project Mission

Build a high-throughput autonomous video Agent workbench for ordinary testable product videos. The system should move from source materials to review packs with low friction, while Owner only reviews key checkpoints. Do not optimize for engineering white-paper perfection when a smaller safe implementation improves throughput.

## Autonomous Authority

Codex is the only development-time executor. Codex may autonomously read the full repository, create task plans, fix ordinary bugs, optimize general rules, refactor non-core helpers, add or update tests, run tests and dry-runs, update necessary README text, make safe selective commits, push `origin/main` safely, continue debugging failed tests, and complete work that does not touch a mandatory Owner Gate.

These normal low-risk actions do not need step-by-step Owner confirmation.

## Mandatory Owner Gates

Codex must stop and produce an Owner Review Packet when a task hits any gate below.

### GATE_HARD_RULE_CHANGE

Changing, deleting, or weakening any hard rule, including `controlled_sdr`, Git Safety, Media Asset Guard, no-auto-publish, and raw videos immutable.
The TikTok 9:16 output rule is a hard rule: final videos and every timeline segment must remain true 9:16 without black bars, stretch, or horizontal inset.

### GATE_ARCHITECTURE_BREAKING_CHANGE

Changing the `agent_state` schema, changing the Runtime Harness core lifecycle, replacing the render kernel, rewriting `actual_render` or `shot_matcher`, or introducing a new core framework or database.

### GATE_EXTERNAL_PROVIDER_ENABLE

First real VLM API enablement, new paid external services, new API keys or meaningful expected spend, or changing TTS/VLM providers.

### GATE_DESTRUCTIVE_ACTION

Deleting or moving media assets, deleting core modules, bulk-cleaning outputs, `reset --hard`, force push, history rewrite, or deleting more than three tracked source files.

### GATE_REAL_BATCH_LAUNCH

First real 50+ Batch2 production run, first real VLM batch QC, or first real generation of 12 or more videos.

### GATE_RELEASE_OR_PUBLISH

Automatic publishing, bulk movement into formal publish directories, or marking candidates as directly deployable.

### GATE_SECURITY_RELAXATION

Any relaxation of media Git shielding, secret protection, or Owner Firewall protections.

## Owner Review Packet

When a mandatory gate is triggered, Codex must stop and output:

```text
OWNER_REVIEW_REQUIRED

checkpoint_id:
checkpoint_type:
current_goal:
completed_work:
proposed_action:
why_owner_approval_is_mandatory:
business_benefit:
affected_files:
hard_rules_affected:
external_provider:
estimated_cost:
estimated_runtime:
expected_video_count:
reversible:
main_risks:
tests_completed:
regression_tests_completed:
git_commit:
git_push_result:
codex_recommendation:
owner_options:
- approve
- reject
- revise
- stop
exact_resume_instruction:
```

Outside mandatory gates, Codex should avoid frequent Owner questions.

For Owner-facing gate output, use Simplified Chinese and present a concrete choice menu. A gate request must include the current problem, why Owner approval is mandatory, completed work, 2-4 executable options, action/benefit/cost/risk/runtime for each option, Codex recommendation and reason, direct Owner reply labels such as `选择 A`, and the exact next command after a valid choice. Do not output vague prompts such as "please confirm", "if no objection", or "recommended to approve" without executable options.

## GPT Consultation Boundary

GPT and chat are consultation mentors for major architecture, business tradeoffs, cost decisions, and high-risk checkpoints. GPT advice is not execution authorization. Only an explicit Owner `approve`, `reject`, `revise`, or `stop` decision can continue or stop gated work.

## Execution Loop

For future tasks, Codex must automatically inspect current state, read this `AGENTS.md`, inspect Git status, define the goal, plan internally, execute safe work, run focused tests, run relevant regressions, check Git Safety, commit coherent source changes, push when safe, update state/evidence, and continue until completion or a mandatory Owner Gate.

Do not ask Owner to manually drive ordinary internal steps.

## Session Resume

Each new Codex session must read `AGENTS.md`, read Git status, read the latest commit, read `agent_state` when present, read the latest Owner decision when present, and infer the safe resume point. Owner should not need to restate full context.

## Single-Writer Data Isolation

Source code is written only by Codex. `agent_state` is written only by Runtime Harness and Owner Firewall. VLM QC reports are written only by VLM Sidecar. Owner decisions are written only through Owner Firewall. Raw materials are read-only. Git receives only source, tests, config templates, and necessary docs. GPT writes no local project data.

## Highest Safety Lines

Videos, images, audio, raw videos, generated outputs, `.xlsx`, `.env`, and API keys must not enter GitHub. `products/**/inputs/raw_videos/**` and `products/**/outputs/**` must stay ignored. Never use `git add .`, force push, destructive history rewrite, automatic publishing, or raw video deletion/move/overwrite.
All TikTok outputs must pass the 9:16 hard guard before review, release, or publish readiness. A final 9:16 container is not enough; each segment must be checked for real vertical canvas, frame fill, black bars, stretch, and semantic crop risk.

## P12E Semantic Compiler Contract

P12D three-variant outputs are negative regression samples for business quality. They must not be deleted and must not be repackaged as success cases. The old P12D free Timeline Planner, filename/order-based planning, no-semantic replacement pool, and remaining nine-video generation are frozen for real runs. P12E entry points must not call the old free Planner.

Every P12E commercial video plan must follow the three-stage protocol: Hook Zone, Core Transaction Zone, and Closure Zone. Core must choose exactly one skeleton: `pain -> intervention -> outcome`, `feature -> demonstration -> proof`, or `situation -> usage -> lifestyle_payoff`. Plans must explain why each visual slot was selected, what claim it supports, and how voiceover maps to visible evidence. Unexplained plans fail and must not render.

The US market output contract is mandatory: `market=US`, `script_language=en-US`, `spoken_language=en-US`, `voice_locale=en-US`, `subtitle_language=en-US`, `fallback_to_system_default=false`, and `allow_windows_sapi_fallback=false`. Edge-TTS failures block audio and hold the variant; Windows SAPI must never be used as a silent fallback for P12E.

Asset semantic indexing may create deterministic candidate windows, keyframe strip plans, and on-demand short proxy plans only under ignored outputs. It must never write sidecars, thumbnails, caches, or cuts into `raw_videos`.

Real VLM semantic labeling requires `GATE_EXTERNAL_PROVIDER_ENABLE` before any media upload, API test, API key use, or paid call. VLM may describe, classify, and score assets, but it must not generate final timelines, publish, modify media, weaken hard rules, or override Owner decisions.

## VIDEO_TRANSITION_ZERO_FREEZE_INVARIANT

Any non-designed freeze immediately before a video transition is a hard failure and must be classified before a final video is accepted.

`PIPELINE_INTRODUCED_FREEZE` means the render pipeline created the freeze through last-frame copying, PTS gaps, repeated CFR normalization, an overlong visual slot, an invalid L-Cut, concat timestamp gaps, final mux duration mismatch, or equivalent behavior. This is always a Hard Failure. A video containing it must not enter a final delivery directory or be reported as complete.

`SOURCE_NATURAL_STATIC` means the source footage itself is already static in the corresponding window. It must not be automatically misclassified as a render failure, but it still requires rhythm and pacing review before acceptance.

`INTENTIONAL_HOLD` is allowed only for clearly marked Hero, Detail, or Closure shots. The slate must contain `intentional_hold = true`, `hold_reason`, `hold_duration_ms`, and `editorial_role`. It must never be used for dynamic action, ordinary transitions, L-Cut padding, or filling an overlong visual slot.

The pipeline must never use `tpad=stop_mode=clone`, frame loops, last-frame image loops, or equivalent clone padding for ordinary video. Ordinary segments must not be extended by copying the final frame. All concat inputs must start at PTS 0, and final outputs must use a single CFR normalization strategy. VLM approval cannot override a local physical frame-detection failure. Every final video must pass transition freeze detection before delivery readiness.
