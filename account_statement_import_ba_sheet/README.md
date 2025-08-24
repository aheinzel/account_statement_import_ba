# Bank Austria Statement Import (XLS/XLSX, strict EUR) — 18.0.3.4.5

Changes:
- Statement name shows date range: **first..last** transaction date (e.g., `2025-07-01..2025-07-31`).
- Statement `date` = last transaction date.
- **No balances**: we do not set `balance_start` or `balance_end_real`.
- `unique_import_id` = SHA1 of `date|amount|BT[:32]` (first 32 chars of Booking Text, after sanitization).
- Keep: `payment_ref` only (no `name`, no `ref`), BT second, both PAYER/PAYEE included, EUR-only, strict headers.

Return shape to OCA wizard:
```
[("EUR", None, [{
  "date": "YYYY-MM-DD",   # last tx date
  "name": "Bank Austria import YYYY-MM-DD..YYYY-MM-DD (EUR)",
  "transactions": [
    {"date": "YYYY-MM-DD", "payment_ref": "...", "amount": <float>, "unique_import_id": "..."}
  ]
}])]
```
