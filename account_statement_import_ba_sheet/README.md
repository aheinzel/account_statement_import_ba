# Bank Austria Statement Import (XLS/XLSX, strict EUR)

**3‑tuple return shape** build (matches your OCA wizard’s expectation):

```
[(currency_code, account_number, [statement_dicts])]
# here: [("EUR", None, [stmt])]
```

Statement keys:
- `date` (ISO string), `name`
- `currency_code`: "EUR"
- `balance_start`: 0.0
- `balance_end_real`: sum of tx amounts
- `transactions`: list of tx dicts

Transaction keys:
- `date` (ISO), `name`, `payment_ref` (same as name), `amount` (float), `unique_import_id`
- optional: `ref`, `partner_name`

Logging:
- `BA sheet: read N data rows`
- `BA sheet: returning 3-tuple payload ...`

Other behavior unchanged: XLS/XLSX only, strict headers, EUR-only rows, `BT` right after `OD`, always include `VD`, replace `|`→`/`, newlines→spaces, full `RD`, no partner auto-create.
