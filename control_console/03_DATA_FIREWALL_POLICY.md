# Data Firewall Policy

## Default Rule

Every product, SKU, batch, and model output must stay in its assigned directory. A module may read shared policy documents but may write only to approved output paths.

## Directory Boundaries

- `control_console/`: read-only by default; writable only with explicit user approval.
- `products/product_slug/`: product-owned source assets and product-level outputs. One product must not write into another product's folder.
- `experiments/product_slug/sku_slug/batch_id/`: batch-owned manual test records. One batch must not write into another batch.
- `project_journal/`: append-only project history, decisions, errors, and changelog notes.
- `scenario_keyword_mining/`: scene words, pain words, hook hypotheses, and reference-mining notes.

## Module Failure Rule

One module failure must not block unrelated modules. Record the failure in the relevant report or journal and continue the MVP path if the remaining system is still usable.

## Traceability Rule

Generated files must be traceable by product, SKU, batch, version, and date whenever applicable.

## Reference Safety

Do not copy reference video captions, original music, original footage, creator identity, or distinctive expression. Mine business-relevant patterns only.
