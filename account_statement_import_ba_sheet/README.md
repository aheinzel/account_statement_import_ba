# Bank Austria Statement Import (XLS/XLSX, strict EUR)

This build adapts the **return shape** to what your `account_statement_import_file` wizard expects:

Return value from `_parse_file` → a **list of tuples**:
```
[(account_number, [statement_dicts...])]
```
We set `account_number = None` (unknown), and wrap the single statement we build.

Statement dict keys (conservative):
- `date` (ISO string), `name` (str)
- `currency_code` = "EUR"
- `balance_start` (float), `balance_end_real` (float)
- `transactions`: list of dicts

Transaction dict keys:
- `date` (ISO string), `name` (str), `payment_ref` (str), `amount` (float), `unique_import_id` (str)
- optional: `ref`, `partner_name`

All previous behavior kept (strict headers, EUR-only, XLS/XLSX only, BT after OD, always include VD, `|`→`/`, newlines→spaces, full RD).

Logs line to confirm shape:
```
BA sheet: returning account/statement tuple with keys=['balance_end_real','balance_start','currency_code','date','name','transactions']
```
