"""Build output/products.csv from prices/params when prom.xml export is unavailable."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
PRODUCTS_PATH = OUTPUT_DIR / "products.csv"

FIELDS = ["offer_id", "sku", "name", "category_id", "brand", "model", "url", "description"]


def _name_from_params(params: dict[str, str], offer_id: str) -> str:
    parts: list[str] = []
    for key in (
        "Производитель",
        "Тип",
        "Вид",
        "Назначение",
        "Форм-фактор",
        "Материал",
        "Модель",
    ):
        v = (params.get(key) or "").strip()
        if not v or len(v) > 120:
            continue
        if v not in " — ".join(parts):
            parts.append(v)
        if len(" — ".join(parts)) > 200:
            break
    base = " — ".join(parts[:4]) if parts else ""
    if len(base) < 3:
        return f"Товар {offer_id}"
    return base[:500]


def _description_from_params(params: dict[str, str], limit: int = 12) -> str:
    lines: list[str] = []
    for name, value in sorted(params.items()):
        if not name or not value:
            continue
        if len(value) > 200:
            continue
        lines.append(f"{name}: {value}")
        if len(lines) >= limit:
            break
    return "\n".join(lines)


def main() -> None:
    params_by_offer: dict[str, dict[str, str]] = {}
    with (OUTPUT_DIR / "params.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            oid = row["offer_id"].strip()
            if not oid:
                continue
            params_by_offer.setdefault(oid, {})[row["param_name"]] = row["param_value"]

    offer_ids: set[str] = set()
    with (OUTPUT_DIR / "prices.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("offer_id"):
                offer_ids.add(row["offer_id"].strip())

    with (OUTPUT_DIR / "media.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("offer_id"):
                offer_ids.add(row["offer_id"].strip())

    offer_ids |= set(params_by_offer.keys())

    rows: list[dict[str, str]] = []
    for oid in sorted(offer_ids):
        p = params_by_offer.get(oid, {})
        brand = (p.get("Производитель") or "").strip()[:255]
        rows.append(
            {
                "offer_id": oid,
                "sku": "",
                "name": _name_from_params(p, oid),
                "category_id": "",
                "brand": brand,
                "model": "",
                "url": "",
                "description": _description_from_params(p),
            }
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with PRODUCTS_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {len(rows)} rows to {PRODUCTS_PATH}")


if __name__ == "__main__":
    main()
