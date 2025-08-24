# Bank Austria Statement Import (XLS/XLSX, strict EUR) — 18.0.3.4.8

**Owner detection: context-only**
- We look up the owner IBAN strictly from the **import context**:
  - `context['journal_id']`, or if opened on a journal: `context['active_model']=='account.journal'` + `context['active_id']`.
- We do **not** look at company bank accounts or other journals.

**Partner selection (still strict)**
- Set `partner_name` only if BOTH PAYER_ACC and PAYEE_ACC are present and **exactly one** equals the owner IBAN from context.
- Otherwise leave partner unset.

**Other behavior unchanged**
- Sorted oldest→newest; statement name shows first..last date; statement date = last.
- No balances included; transactions use `payment_ref` only (BT second, both parties included), EUR-only rows, strict headers.
