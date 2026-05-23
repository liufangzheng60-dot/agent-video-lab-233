# Master Control

## Authority

The user is the highest decision maker for this workspace.

No model, helper script, or automation module may override product strategy, publish decisions, data firewall rules, or scope boundaries without explicit user approval.

## Operating Principle

- Build toward the TikTok Shop product video MVP.
- Keep product, SKU, batch, and model outputs isolated.
- Prefer traceable, reversible, manually reviewable steps.
- Do not optimize one module by corrupting another module's data.

## Approval Rule

`control_console/` is read-only by default. It may be modified only when the user explicitly approves a control, policy, registry, or queue update task.
