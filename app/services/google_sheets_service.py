"""Escritura de cotizaciones en la pestaña Ventas de Google Sheets."""

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from app.config.settings import settings


SALES_SHEET_TITLE = "STOCK"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SHEET_COLUMNS = [
    ("tipo", "FINAL, TIENDA", {"FINALTIENDA", "TIPO"}),
    ("departamento", "DPTO", {"DPTO", "DEPARTAMENTO"}),
    ("provincia", "PROVI.", {"PROVI", "PROVINCIA", "PROVI1", "PROVINCIA1"}),
    (
        "provincia_adicional",
        "PROVI.",
        {
            "PROVI",
            "PROVINCIA",
            "PROVI2",
            "PROVINCIA2",
            "SEGUNDAPROVINCIA",
            "PROVINCIAADICIONAL",
        },
    ),
    ("agencia", "AGENCIA", {"AGENCIA"}),
    ("olva", "OLVA", {"OLVA"}),
    ("frank", "FRANK", {"FRANK"}),
    ("vendedor", "VEND.", {"VEND", "VENDEDOR"}),
    ("dni", "DNI", {"DNI"}),
    ("numero", "N°", {"N", "NRO", "NUMERO", "NUMERODEVENTA", "NVENTA"}),
    ("cliente", "CLIENTE", {"CLIENTE", "NOMBRECLIENTE"}),
    ("telefono", "TELEFONO", {"TELEFONO", "TELEFONOCLIENTE", "PHONE"}),
    ("fecha_venta", "FECHA V.", {"FECHAV", "FECHAVENTA", "FECHA"}),
    ("precio_final", "PRECIO F.", {"PRECIOF", "PRECIOFINAL"}),
    ("envio", "ENVIO", {"ENVIO"}),
    ("accesorio", "ACCES.", {"ACCES", "ACCESORIO"}),
    ("banco", "BANCO", {"BANCO"}),
    ("total", "S/. TOTAL", {"STOTAL", "TOTAL", "TOTALS"}),
]

SERIAL_HEADER_ALIASES = {"SERIE", "SERIAL", "SERIENUMBER"}


def _normalize_header(value: str) -> str:
    without_accents = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(char for char in without_accents if not unicodedata.combining(char))
    return re.sub(r"[^A-Z0-9]", "", ascii_value.upper())


def _get_google_sheets_client():
    credentials_config = settings.GOOGLE_CREDS_JSON
    if not credentials_config:
        raise RuntimeError("Falta configurar GOOGLE_SHEETS_CREDENTIALS.")
    if not settings.SHEET_ID:
        raise RuntimeError("Falta configurar GOOGLE_SHEET_ID.")

    import gspread
    from google.oauth2.service_account import Credentials

    if credentials_config.lstrip().startswith("{"):
        credentials_info = json.loads(credentials_config)
        credentials = Credentials.from_service_account_info(
            credentials_info,
            scopes=SCOPES,
        )
    else:
        credentials_path = Path(credentials_config).expanduser()
        if not credentials_path.is_file():
            raise FileNotFoundError(
                "No se encontró el archivo de credenciales de Google Sheets."
            )
        credentials = Credentials.from_service_account_file(
            str(credentials_path),
            scopes=SCOPES,
        )

    return gspread.authorize(credentials)


def update_sales_rows_by_serial(items: list[dict[str, Any]]) -> None:
    """Actualiza las filas existentes en Ventas usando la serie como clave."""
    from gspread.utils import rowcol_to_a1

    if not items:
        raise ValueError("La cotización no contiene productos con series para actualizar.")

    spreadsheet = _get_google_sheets_client().open_by_key(settings.SHEET_ID)
    worksheet = spreadsheet.worksheet(SALES_SHEET_TITLE)

    headers = worksheet.row_values(1)
    normalized_headers = [_normalize_header(header) for header in headers]
    serial_matches = [
        index for index, header in enumerate(normalized_headers)
        if header in SERIAL_HEADER_ALIASES
    ]
    if len(serial_matches) != 1:
        raise ValueError(
            "La pestaña Ventas debe tener exactamente una columna SERIE."
        )
    serial_column = serial_matches[0]

    header_indexes: dict[str, int] = {}
    used_indexes: set[int] = set()

    for field, title, aliases in SHEET_COLUMNS:
        index = next(
            (
                i
                for i, header in enumerate(headers)
                if i not in used_indexes and _normalize_header(header) in aliases
            ),
            None,
        )
        if index is None:
            raise ValueError(
                f"No se encontró la columna requerida {title} en la pestaña Ventas."
            )
        header_indexes[field] = index
        used_indexes.add(index)

    sheet_rows = worksheet.get_all_values()
    serial_row_indexes: dict[str, list[int]] = {}
    for row_index, row in enumerate(sheet_rows[1:], start=2):
        serial = row[serial_column].strip() if serial_column < len(row) else ""
        if serial:
            serial_row_indexes.setdefault(serial, []).append(row_index)

    planned_updates: list[dict[str, Any]] = []
    seen_serials: set[str] = set()
    for item in items:
        serial = str(item.get("serie") or "").strip()
        if not serial:
            raise ValueError("Un producto seleccionado no tiene número de serie.")
        if serial in seen_serials:
            raise ValueError(f"La serie {serial} está repetida en la cotización.")
        seen_serials.add(serial)

        matching_rows = serial_row_indexes.get(serial, [])
        if len(matching_rows) != 1:
            if not matching_rows:
                raise ValueError(f"No se encontró la serie {serial} en la pestaña Ventas.")
            raise ValueError(f"La serie {serial} aparece más de una vez en la pestaña Ventas.")

        row_number = matching_rows[0]
        for field, column_index in header_indexes.items():
            value = item.get(field)
            cell = rowcol_to_a1(row_number, column_index + 1)
            planned_updates.append({
                "range": cell,
                "values": [["" if value is None else value]],
            })

    if planned_updates:
        worksheet.batch_update(planned_updates, value_input_option="RAW")
