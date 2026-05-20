# P0-002 Material Pack

## Goal

Build an Agent-readable material pack from local material inventory and product brief files.

## Inputs

- `outputs/material_inventory/material_inventory.json`
- `inputs/product_briefs/*.txt`
- `inputs/product_briefs/*.md`

## Outputs

- `outputs/material_pack/material_pack.json`
- `outputs/material_pack/material_pack.md`

## Command

```bash
python main.py material-pack
```

## Scope

- Reads local inventory JSON.
- Reads local product brief text files.
- Assigns `suggested_role` for each material.
- Adds basic video risk flags, including `aspect_ratio_not_9_16`.
- Does not do AI visual understanding.
- Does not transcribe video.
- Does not edit or render video.
- Does not call external APIs.
- Does not install dependencies.
