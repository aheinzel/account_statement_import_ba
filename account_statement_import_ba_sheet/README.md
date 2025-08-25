# Bank Austria Statement Import (XLS/XLSX, strict EUR) — Odoo 18 CE

> **Disclaimer:** This module was auto-generated with OpenAI ChatGPT (GPT-5) as part of a personal experiment to evaluate how GPT-5 can assist with software development. It is provided "as is," without warranty of any kind. I’m using it as a learning exercise; please review, adapt, and test thoroughly in a non-production environment before use (if you really must).


## Overview

Adds a **Bank Austria**-specific **Excel (XLS/XLSX)** parser to the OCA wizard **`Accounting → (Bank Journal) → Import Statement`**. It consumes the bank‑exported Excel with fixed headers and produces a statement for Odoo’s reconciliation flow. **CSV support is intentionally excluded.**

## Hard Requirements

* **Odoo:** 18 CE
* **OCA module:** `account_statement_import_file` (provides the `account.statement.import` wizard this parser plugs into)

## Optional (Recommended)

* **OCA:** `account_reconcile_oca` – enhances/streamlines manual reconciliation after the import.

## External Python Dependencies

* **`openpyxl`** (for `.xlsx`)
* **`xlrd<2.0`** (only if you still import legacy `.xls`)

> Install these in your Odoo environment (container or venv). In Docker, you can bake them into the image or mount them into the Python path.

## Installation

1. Copy the module folder **`account_statement_import_ba_sheet/`** to your addons path (e.g., `/mnt/extra-addons/`).
2. Ensure the dependencies above are available.
3. Update the Apps list and install **“Bank Austria Statement Import (XLS/XLSX, strict EUR)”**.

## Usage

1. Open your **Bank** journal (the one you want to import into).
2. Click **Import Statement**.
3. Select the **Bank Austria** Excel export (`.xlsx` or `.xls`) with the required header line.
4. The wizard shows the resulting statement; confirm to create it.

## Input Format (Headers)

**Required (exact labels, case-insensitive):**

* `Operation date`
* `Value Date`
* `Booking text`
* `Internal Note`
* `Currency`
* `Amount`

**Optional (if present, will be used):**

* `Record data`
* `Record Number`
* `Payer Name`
* `Payer Account`
* `Payer Bank Code`
* `Payee Name`
* `Payee Account`
* `Payee Bank Code`
* `Purpose Text`
* `Reference`

> **Currency:** Only **EUR** rows are accepted. Non‑EUR rows abort the import with a clear error.

## Behavior & Conventions

* **Sanitization:** Replace `|` → `/`; replace newlines with spaces and collapse duplicate spaces. Always include `VD` in the line description.

* **`payment_ref` only:** Statement **lines** use `payment_ref` (description) exclusively — no `name`, no `ref`.

* **Parseable description order:**

  ```
  DIR=IN|OUT | BT=<Booking text> | OD=<Operation date> | VD=<Value date> | CUR=EUR | AMT=<amount>
  | PAYER=<payer> | PAYER_ACC=<payer acc> | PAYER_BC=<payer bc>
  | PAYEE=<payee> | PAYEE_ACC=<payee acc> | PAYEE_BC=<payee bc>
  | PT=<purpose> | REF=<reference/record number> | RD=<record data>
  ```

* **Abbreviations**

  | Key                                   | Meaning                               |
  | ------------------------------------- | ------------------------------------- |
  | `DIR`                                 | Direction (`IN`/`OUT`)                |
  | `BT`                                  | Booking Text                          |
  | `OD`                                  | Operation Date                        |
  | `VD`                                  | Value Date (Valuta)                   |
  | `CUR`                                 | Currency (EUR enforced)               |
  | `AMT`                                 | Amount                                |
  | `PAYER(_ACC/_BC)` / `PAYEE(_ACC/_BC)` | Names/Accounts/Bank codes as provided |
  | `PT`                                  | Purpose Text                          |
  | `REF`                                 | Reference (or Record Number)          |
  | `RD`                                  | Record Data                           |

* **Partner (Kunde) assignment – strict, context‑only:**

  * The importer determines **your own IBAN** from the import **context** only (the active bank journal in the wizard).
  * We set **no partner** unless **both** `PAYER_ACC` and `PAYEE_ACC` are present **and exactly one** equals your IBAN. In that case we set the partner **name** to the **other** side. We never set `partner_id` or auto‑create a contact.

* **Ordering:** Lines are sorted **oldest → newest** before creating the statement.

* **Statement naming:** The statement title includes the **date range**: `Bank Austria import YYYY-MM-DD..YYYY-MM-DD (EUR)` (single date if only one day).

* **Statement date:** Set to the **last** transaction date.

* **Balances:** We **do not** set `balance_start` / `balance_end_real`.

* **Deduplication:** `unique_import_id = sha1("<date>|<amount>|<BT[:32]>")` to avoid accidental re‑imports.

* **Logging:** Normal operation logs are **DEBUG** only; user‑visible errors are raised as `UserError`.

## Troubleshooting

* **“Missing required columns”** → Verify the first line of your Excel matches the required headers exactly.
* **“Non‑EUR row detected”** → The file contains a currency other than EUR; filter or export an EUR‑only file.
* **Partner not set** → This is expected if the wizard context doesn’t point to a bank journal with an IBAN or if both sides’ accounts are missing/ambiguous.
* **Legacy `.xls` fails** → Install `xlrd<2.0` or export as `.xlsx`.

## Compatibility

* Designed for **Odoo 18 CE**; tested against OCA `account_statement_import_file` wizard. Other statement import add‑ons are not required.
