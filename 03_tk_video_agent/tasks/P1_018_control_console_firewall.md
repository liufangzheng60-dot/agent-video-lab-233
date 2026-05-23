# P1-018 Control Console Firewall And Scenario Keyword System

## Goal

Create governance templates for a multi-model, multi-product, multi-SKU workspace:

- `control_console/`
- `project_journal/`
- `scenario_keyword_mining/`

## Control Console

The control console records:

- User authority as highest decision maker.
- Active sprint: `dog_bath_hose / blue`.
- Model role contracts.
- Data firewall policy.
- Module registry.
- Decision log.
- Do-not-touch rules.
- Next action queue.

## Data Firewall

- `control_console/` is read-only by default unless explicitly approved.
- Different `products/product_slug/` folders must not cross-write.
- Different `experiments/product/sku/batch/` folders must not cross-write.
- Model outputs must stay inside assigned outputs or reports.
- One module failure must not block unrelated modules.
- Generated files should be traceable by product, SKU, batch, version, and date.

## Scenario Keyword Mining

Reference mining should produce:

- Scene words
- Pain words
- Emotion triggers
- Hook hypotheses
- Demonstration logic
- Differentiated selling points

It must not copy reference captions, original music, original footage, creator identity, or distinctive expression.

Every optimization idea should include:

- Business purpose
- Metric impact
- First-principles reason

## Scope

- No video generation.
- No rendering.
- No ffmpeg call.
- No external API call.
- No dependency installation.
- No GitHub push handling.
- No modification of existing product source assets.
