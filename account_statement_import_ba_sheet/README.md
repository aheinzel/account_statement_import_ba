# Bank Austria Statement Import (XLS/XLSX, strict EUR) — 18.0.3.4.4

**Partner selection (strict)**
- Set `partner_name` **only** when **both** `PAYER_ACC` and `PAYEE_ACC` are present **and**
  **exactly one** equals your journal’s own account number (IBAN). In that case, we use the other side’s name.
- In all other cases (missing owner IBAN, missing either account, neither matches owner, or both match), we **do not** set any partner.

**payment_ref**
- Still includes **both** parties as provided in the Excel (after basic sanitization), with the fixed key order:  
  `DIR → BT → OD → VD → CUR → AMT → PAYER → PAYER_ACC → PAYER_BC → PAYEE → PAYEE_ACC → PAYEE_BC → PT → REF → RD`.

**Other notes**
- Transactions carry **`payment_ref`** only (no `name`) and **no `ref`**.
- EUR-only rows; strict required headers; XLS & XLSX support (requires `openpyxl` for XLSX; `xlrd<2.0` if you need legacy XLS).
- Returns `[("EUR", None, [statement_dict])]` for the OCA wizard.

**Abbreviations**
- `DIR` direction, `BT` booking text, `OD` operation date, `VD` value date, `CUR` currency, `AMT` amount,
  `PAYER(_ACC/_BC)`, `PAYEE(_ACC/_BC)`, `PT` purpose text, `REF` reference, `RD` record data.
