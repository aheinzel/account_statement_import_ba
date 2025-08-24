# Bank Austria Statement Import (XLS/XLSX, strict EUR)

Bank Austria–specific statement importer for **Odoo 18 CE**, plugging into OCA
`account_statement_import_file`. It accepts **only Excel** (XLSX/XLS) and enforces:

- **Strict headers** (no synonyms). Required columns:  
  `Operation date`, `Value Date`, `Booking text`, `Internal Note`, `Currency`, `Amount`  
  Optional: `Record data`, `Record Number`, `Payer Name`, `Payer Account`, `Payer Bank Code`,  
  `Payee Name`, `Payee Account`, `Payee Bank Code`, `Purpose Text`, `Reference`
- **EUR-only**: all rows must be `EUR` (or `€`), and the selected journal must be in EUR.
- **Fixed, parsable Buchungstext** stored in `name` with stable key=value sections. **BT follows OD**.  
  Values sanitize newlines (to spaces, deduped) and **replace '|' with '/'** so the pipe can be used as a field separator without escapes.

Format:
```
DIR=IN|OUT | OD=YYYY-MM-DD | BT=… | VD=YYYY-MM-DD | CUR=EUR | AMT=±#.## | CP=… | CP_ACC=… | CP_BC=… | PT=… | REF=… | RD=…
```
## Install
1. Ensure **`account_statement_import_file`** is installed.
2. `pip install openpyxl` (and `pip install "xlrd<2.0"` for old `.xls` if needed).
3. Copy this module to your `addons_path`, update apps, and install.
4. Use **Accounting → Configuration → Journals → [Bank] → Import Statement**.

## Notes
- `partner_name` is set from **Payer Name** (incoming) or **Payee Name** (outgoing); the module does not create partners.
- Duplicate protection uses a SHA1 of OD, VD, amount, booking text, purpose text, ref, and record data.
