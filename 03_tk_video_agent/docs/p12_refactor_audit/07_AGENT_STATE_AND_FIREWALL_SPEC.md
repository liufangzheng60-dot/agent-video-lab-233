# Agent State And Firewall Spec

## agent_state.json Requirements

`agent_state.json` must support:

- current `batch_id`
- current `product`
- current `sku`
- `variants_requested`
- `variants_generated`
- `current_stage`
- `stage_status`
- `hard_rule_results`
- `vlm_qc_results`
- `owner_firewall_status`
- `output_paths`
- `failed_variants`
- `rerun_history`
- `final_review_pack_path`
- input and output paths per stage
- hard rule gate result per stage
- VLM result per variant
- Owner decision per variant
- rerun count
- deletion audit
- negative memory update
- failed stage recovery
- `resume_from_stage`
- immutable asset protection status

## owner_firewall_decisions.json Requirements

Supported actions:

- `approve_all`
- `approve_selected`
- `force_reject`
- `force_delete_candidate`
- `force_rerun_variant`
- `force_stop_pipeline`
- `force_override_vlm`
- `force_write_negative_example`

## Owner Firewall Principles

Owner is the highest decision layer. No VLM, LLM, or Runtime Agent may bypass Owner into automatic publishing.

Owner can force delete candidates, force rerun, and force override VLM judgment. All Owner operations must be written to disk as audit log entries.

## Failed Stage Recovery

Each stage must write enough state to resume safely. Failed stages should not require the Owner to reconstruct context from chat history.

## Immutable Asset Protection

Raw videos are immutable. Runtime stages may read them, but must not move, delete, rename, or rewrite them.
