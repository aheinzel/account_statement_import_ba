# Bank Austria Statement Import (XLS/XLSX, strict EUR)

**Fix:** Remove `currency_code` from the statement dict and `payment_ref` from tx lines.
Wizard still gets currency via 3‑tuple header: `("EUR", account_number, [stmts])`.

Return shape from `_parse_file`:
```
[("EUR", None, [{
  "date": "YYYY-MM-DD",
  "name": "...",
  "balance_start": 0.0,
  "balance_end_real": <sum>,
  "transactions": [
    {"date": "YYYY-MM-DD", "name": "...", "amount": <float>, "unique_import_id": "...", "ref": "...", "partner_name": "..."}
  ]
}] )]
```

Other behavior unchanged: strict headers, EUR-only, XLS/XLSX only, BT after OD, always include VD, `|`→`/`, newlines→spaces, full RD, no partner auto-create.
