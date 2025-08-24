# Bank Austria Statement Import (XLS/XLSX, strict EUR) — Diagnostic Build

Adds extra logging to understand "Diese Datei enthält keinen Vorgang" cases.

- Logs tx **count**, **sum**, and the **first 3 tx** (date, amount, name, uid)
- Returns the 3‑tuple that your wizard expects: `[("EUR", None, [stmt])]`
- Statement keys: `date`, `name`, `balance_start`, `balance_end_real`, `transactions`
- Tx keys: `date`, `name`, `amount`, `unique_import_id` (+ optional `ref`, `partner_name`)

Everything else unchanged (strict headers, EUR-only rows, XLS/XLSX only, BT after OD, always include VD, `|`→`/`, newlines→spaces, full RD).

If the wizard still says "no operation", compare our logged **uids** with existing statement lines — they may all be deduplicated by the wizard.
