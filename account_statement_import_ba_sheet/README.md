# Bank Austria Statement Import (XLS/XLSX, strict EUR) — 18.0.1.0.0

- Owner account detection: **context-only** (`journal_id` / `active_id`), no cross-company scan.
- Partner set **only** if both payer & payee accounts are present and exactly one equals the owner IBAN.
- Lines sorted oldest→newest; statement name shows date range (first..last); statement date = last.
- No balances in payload; transactions use **payment_ref only** (BT second; both parties included, sanitized `|`→`/`, newlines→spaces).
- EUR-only rows; strict required headers; handles both `.xls` (needs `xlrd<2.0`) and `.xlsx` (needs `openpyxl`).

Install: drop into `/mnt/extra-addons/`, update apps, restart Odoo.
