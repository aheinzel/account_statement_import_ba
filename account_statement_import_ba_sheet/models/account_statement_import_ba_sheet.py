import base64
import io
import logging
from datetime import datetime, date
from typing import Dict, Optional

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# ---- Strict header lists (case-insensitive, exact labels only; no synonyms) ----
REQUIRED_HEADERS = [
    "operation date",
    "value date",
    "booking text",
    "internal note",
    "currency",
    "amount",
]

OPTIONAL_HEADERS = [
    "record data",
    "record number",
    "payer name",
    "payer account",
    "payer bank code",
    "payee name",
    "payee account",
    "payee bank code",
    "purpose text",
    "reference",
]

ALL_HEADERS = REQUIRED_HEADERS + OPTIONAL_HEADERS

def _norm(s: str) -> str:
    # normalize header: trim, collapse internal spaces to single space, lowercase
    s = (s or "").strip()
    s = " ".join(s.split())
    return s.lower()

def _excel_kind(content: bytes) -> Optional[str]:
    sig_xlsx = bytes([0x50, 0x4B, 0x03, 0x04])  # ZIP 'PK..'
    sig_xls  = bytes([0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1])  # OLE CFBF
    if content[:4] == sig_xlsx:
        return "xlsx"
    if content[:8] == sig_xls:
        return "xls"
    return None

_DATE_PATTERNS = ["%Y-%m-%d","%d.%m.%Y","%d.%m.%y","%Y/%m/%d","%d/%m/%Y","%m/%d/%Y"]

def _to_iso_date(val) -> str:
    """Best-effort to get YYYY-MM-DD; returns string always."""
    if isinstance(val, datetime):
        return val.date().isoformat()
    if isinstance(val, date):
        return val.isoformat()
    s = (str(val or "").strip())
    for fmt in _DATE_PATTERNS:
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except Exception:
            pass
    # Already iso-like?
    try:
        return datetime.fromisoformat(s).date().isoformat()
    except Exception:
        return s  # as-is; Odoo will validate later

def _parse_number(val) -> float:
    if val in (None, ""):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace("\xa0"," ")
    s = s.replace(" ", "")
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".","").replace(",",".")
        else:
            s = s.replace(",","")
    elif "," in s:
        s = s.replace(".","").replace(",",".")
    try:
        return float(s)
    except Exception:
        import re
        s2 = re.sub(r"[^0-9\.-]","", s)
        return float(s2) if s2 else 0.0

def _format_amount(val: float) -> str:
    return f"{val:.2f}"

def _sanitize_val(v):
    """Replace newlines with spaces (collapse to single spaces) and replace '|' with '/'."""
    if v is None:
        return None
    s = str(v).replace("\r", " ").replace("\n", " ")
    s = " ".join(s.split())  # collapse whitespace
    s = s.replace("|", "/")
    s = s.strip()
    return s if s else None

def _build_name(row: Dict[str, object], amount: float, op_date_iso: str, val_date_iso: str) -> str:
    # Fixed, key=value pipeline; **BT placed immediately after OD**; always include VD
    direction = "IN" if amount >= 0 else "OUT"
    # Counterparty based on direction
    if amount >= 0:
        cp = _sanitize_val(row.get("payer name"))
        cp_acc = _sanitize_val(row.get("payer account"))
        cp_bc = _sanitize_val(row.get("payer bank code"))
    else:
        cp = _sanitize_val(row.get("payee name"))
        cp_acc = _sanitize_val(row.get("payee account"))
        cp_bc = _sanitize_val(row.get("payee bank code"))

    pieces = []
    pieces.append(f"DIR={direction}")
    pieces.append(f"OD={op_date_iso}")
    # Booking text right after OD
    bt = _sanitize_val(row.get("booking text"))
    if bt:
        pieces.append(f"BT={bt}")
    pieces.append(f"VD={val_date_iso}")
    pieces.append(f"CUR={_sanitize_val(row.get('currency')) or 'EUR'}")
    pieces.append(f"AMT={_format_amount(amount)}")
    if cp:
        pieces.append(f"CP={cp}")
    if cp_acc:
        pieces.append(f"CP_ACC={cp_acc}")
    if cp_bc:
        pieces.append(f"CP_BC={cp_bc}")
    pt = _sanitize_val(row.get("purpose text"))
    if pt:
        pieces.append(f"PT={pt}")
    ref = _sanitize_val(row.get("reference")) or _sanitize_val(row.get("record number"))
    if ref:
        pieces.append(f"REF={ref}")
    rd = _sanitize_val(row.get("record data"))
    if rd is not None:  # include untrimmed; no dedupe
        pieces.append(f"RD={rd}")
    return " | ".join(pieces)

class AccountStatementImportBASheet(models.TransientModel):
    _inherit = "account.statement.import"

    def _parse_file(self, data_file):
        content = data_file if isinstance(data_file, bytes) else base64.b64decode(data_file)
        kind = _excel_kind(content)
        if kind is None:
            return super()._parse_file(data_file)  # not ours

        # Enforce EUR journal
        if hasattr(self, "journal_id") and self.journal_id:
            j_cur = self.journal_id.currency_id or self.journal_id.company_id.currency_id
            if not j_cur or j_cur.name != "EUR":
                raise UserError(_("This importer requires an EUR journal. Selected journal currency is '%s'.") % (j_cur and j_cur.name or "unknown"))

        rows, header_idx = self._read_excel_rows_strict(content, kind)
        _logger.info("BA sheet: read %d data rows from Excel.", len(rows))

        # Build transactions
        txs = []
        bad_currency_rows = []
        for r in rows:
            # Currency enforcement (row-level)
            currency = str(r.get("currency") or "").strip().upper()
            if currency not in ("EUR", "€"):
                bad_currency_rows.append(currency or "?")
                continue

            amount = _parse_number(r.get("amount"))
            op_date_iso = _to_iso_date(r.get("operation date"))
            val_date_iso = _to_iso_date(r.get("value date"))
            name = _build_name(r, amount, op_date_iso, val_date_iso)

            # partner_name only (do not create partners)
            partner_name = None
            if amount >= 0 and r.get("payer name"):
                partner_name = str(r.get("payer name") or "").strip()
            elif amount < 0 and r.get("payee name"):
                partner_name = str(r.get("payee name") or "").strip()

            # Reference: prefer 'Reference' else 'Record Number'
            ref = (r.get("reference") or r.get("record number") or None)
            ref = str(ref).strip() if ref else None

            # Unique ID built on core fields (not truncated)
            uid_seed = f"{op_date_iso}|{val_date_iso}|{amount}|{r.get('booking text')}|{r.get('purpose text')}|{ref or ''}|{r.get('record data') or ''}"
            import hashlib
            unique_import_id = hashlib.sha1(uid_seed.encode("utf-8")).hexdigest()

            tx = {
                "date": op_date_iso or datetime.today().date().isoformat(),
                "name": name or _("Bank transaction"),
                "amount": float(amount),
                "unique_import_id": unique_import_id,
            }
            if ref:
                tx["ref"] = ref
            if partner_name:
                tx["partner_name"] = partner_name
            txs.append(tx)

        if bad_currency_rows:
            raise UserError(_("Non-EUR rows detected. All rows must have Currency = EUR. Offending currencies: %s") % ", ".join(sorted(set(bad_currency_rows))))

        if not txs:
            raise UserError(_("No transactions found after validation. Check required headers and that Currency is EUR on each row."))

        stmt_date = max(tx["date"] for tx in txs if tx.get("date")) or datetime.today().date().isoformat()
        stmt_vals = {
            "date": stmt_date,
            "transactions": txs,
            "name": _("Bank Austria import %s (EUR)") % stmt_date,
        }
        _logger.info("BA sheet: built %d transactions, statement date %s.", len(txs), stmt_date)
        return [stmt_vals]

    def _read_excel_rows_strict(self, content: bytes, kind: str):
        # Read first sheet, map only declared headers; fail if required headers missing.
        if kind == "xlsx":
            try:
                from openpyxl import load_workbook
            except Exception as e:
                raise UserError(_("Missing python dependency 'openpyxl' to read XLSX: %s") % e)
            wb = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
            ws = wb.worksheets[0]
            it = ws.iter_rows(values_only=True)
            try:
                headers = [str(h or "").strip() for h in next(it)]
            except StopIteration:
                raise UserError(_("Empty Excel file."))
            norm = [_norm(h) for h in headers]
            idx = {}
            for i, h in enumerate(norm):
                if h in ALL_HEADERS:
                    idx[h] = i
            missing = [h for h in REQUIRED_HEADERS if h not in idx]
            if missing:
                raise UserError(_("Missing required columns: %s") % ", ".join(missing))
            rows = []
            for row in it:
                if not any(v not in (None, "") for v in row):
                    continue
                rec: Dict[str, object] = {}
                for key, col in idx.items():
                    if col < len(row):
                        rec[key] = row[col]
                rows.append(rec)
            return rows, idx
        else:  # xls
            try:
                import xlrd  # xlrd<2.0
            except Exception as e:
                raise UserError(_("To read legacy .XLS files, install 'xlrd<2.0' or export as XLSX. Error: %s") % e)
            book = xlrd.open_workbook(file_contents=content)
            sheet = book.sheet_by_index(0)
            if sheet.nrows == 0:
                raise UserError(_("Empty Excel file."))
            headers = [str(sheet.cell_value(0, c)).strip() for c in range(sheet.ncols)]
            norm = [_norm(h) for h in headers]
            idx = {}
            for i, h in enumerate(norm):
                if h in ALL_HEADERS:
                    idx[h] = i
            missing = [h for h in REQUIRED_HEADERS if h not in idx]
            if missing:
                raise UserError(_("Missing required columns: %s") % ", ".join(missing))
            rows = []
            for r in range(1, sheet.nrows):
                if not any((str(sheet.cell_value(r, c)) if sheet.cell_value(r, c) is not None else "").strip() for c in range(sheet.ncols)):
                    continue
                rec: Dict[str, object] = {}
                for key, col in idx.items():
                    val = sheet.cell_value(r, col)
                    if key in ("operation date", "value date") and sheet.cell_type(r, col) == 3:
                        val = xlrd.xldate_as_datetime(val, book.datemode)
                    rec[key] = val
                rows.append(rec)
            return rows, idx
