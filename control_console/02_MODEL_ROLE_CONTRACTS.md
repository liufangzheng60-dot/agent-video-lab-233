# Model Role Contracts

## Codex

- Writes and tests local code, templates, structured docs, and project files.
- Must respect allowed file lists and product/batch isolation.
- Must not call external APIs unless explicitly approved.

## Claude

- May be used for strategy critique, copy evaluation, reasoning, and planning.
- Should write only to approved reports or decision documents.
- Must not modify product source assets or code without explicit routing through the approved workflow.

## Seedance

- Generates video or visual material only when the user explicitly requests asset generation.
- Outputs must be saved under the assigned product and batch paths.
- Must not overwrite source assets or cross-write between products.

## Audio API

- Generates or processes audio only when explicitly approved.
- Outputs must be isolated by product, SKU, batch, and version.
- Must not be used for unapproved scraping, cloning, or platform automation.

## Reference Mining

- Extracts scene words, pain words, emotion triggers, demonstration logic, and hook hypotheses.
- Must not copy reference video captions, music, footage, or creator-specific expression.
- Outputs belong under `scenario_keyword_mining/` or approved reports.
