# Bank Austria Statement Import (XLS/XLSX, strict EUR)

Debug-friendly build:
- Returns **date objects** for tx/statement dates
- Adds `currency_code = "EUR"`
- Logs `BA sheet: ...` messages so you can follow the flow

Everything else as agreed (strict headers, EUR-only, XLS/XLSX only, BT after OD, always include VD, `|`→`/`, newlines→spaces, full RD).

Install:
1) Unzip to `/mnt/extra-addons/account_statement_import_ba_sheet/`
2) `chown -R odoo:odoo /mnt/extra-addons`
3) Update Apps, then import via the Journal's **Import Statement**.
