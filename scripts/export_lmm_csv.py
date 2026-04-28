from __future__ import annotations

import csv
import html
import random
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from uk_translations import CATEGORIES_UK, PARAMS_UK

ROOT = Path(__file__).resolve().parents[1]
XML_PATH = ROOT / "data" / "raw" / "prom.xml"
OUTPUT_DIR = ROOT / "output"


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    text = html.unescape(value)
    text = re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()
    return text


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tree = ET.parse(XML_PATH)
    root = tree.getroot()
    shop = root.find("shop")
    if shop is None:
        raise ValueError("XML does not contain <shop> node")

    categories_node = shop.find("categories")
    offers_node = shop.find("offers")
    if categories_node is None or offers_node is None:
        raise ValueError("XML does not contain required categories/offers nodes")

    categories_rows: list[dict[str, str]] = []
    for category in categories_node.findall("category"):
        raw_name = normalize_text(category.text)
        categories_rows.append(
            {
                "category_id": normalize_text(category.get("id")),
                "parent_id": normalize_text(category.get("parentId")),
                "category_name": CATEGORIES_UK.get(raw_name, raw_name),
            }
        )

    products_rows: list[dict[str, str]] = []
    prices_rows: list[dict[str, str]] = []
    media_rows: list[dict[str, str]] = []
    params_rows: list[dict[str, str]] = []

    offer_ids: set[str] = set()
    duplicate_offer_ids: list[str] = []

    for offer in offers_node.findall("offer"):
        offer_id = normalize_text(offer.get("id"))
        if not offer_id:
            continue
        if offer_id in offer_ids:
            duplicate_offer_ids.append(offer_id)
        offer_ids.add(offer_id)

        name = (
            normalize_text(offer.findtext("name_ua"))
            or normalize_text(offer.findtext("name"))
        )
        url = normalize_text(offer.findtext("url"))
        price = normalize_text(offer.findtext("price"))
        old_price = normalize_text(offer.findtext("oldprice"))
        currency = normalize_text(offer.findtext("currencyId"))
        category_id = normalize_text(offer.findtext("categoryId"))
        vendor = normalize_text(offer.findtext("vendor"))
        model = normalize_text(offer.findtext("model"))
        sku = normalize_text(offer.findtext("vendorCode"))
        description = (
            normalize_text(offer.findtext("description_ua"))
            or normalize_text(offer.findtext("description"))
        )
        availability = normalize_text(offer.get("available"))

        products_rows.append(
            {
                "offer_id": offer_id,
                "sku": sku,
                "name": name,
                "category_id": category_id,
                "brand": vendor,
                "model": model,
                "url": url,
                "description": description,
            }
        )

        prices_rows.append(
            {
                "offer_id": offer_id,
                "price": price,
                "old_price": old_price,
                "currency": currency,
                "availability": availability,
            }
        )

        pictures = [normalize_text(node.text) for node in offer.findall("picture")]
        for image_order, image_url in enumerate([item for item in pictures if item], start=1):
            media_rows.append(
                {"offer_id": offer_id, "image_url": image_url, "image_order": str(image_order)}
            )

        for param in offer.findall("param"):
            raw_param_name = normalize_text(param.get("name"))
            params_rows.append(
                {
                    "offer_id": offer_id,
                    "param_name": PARAMS_UK.get(raw_param_name, raw_param_name),
                    "param_value": normalize_text(param.text),
                }
            )

    write_csv(
        OUTPUT_DIR / "categories.csv",
        ["category_id", "parent_id", "category_name"],
        categories_rows,
    )
    write_csv(
        OUTPUT_DIR / "products.csv",
        ["offer_id", "sku", "name", "category_id", "brand", "model", "url", "description"],
        products_rows,
    )
    write_csv(
        OUTPUT_DIR / "prices.csv",
        ["offer_id", "price", "old_price", "currency", "availability"],
        prices_rows,
    )
    write_csv(
        OUTPUT_DIR / "media.csv",
        ["offer_id", "image_url", "image_order"],
        media_rows,
    )
    write_csv(
        OUTPUT_DIR / "params.csv",
        ["offer_id", "param_name", "param_value"],
        params_rows,
    )

    category_ids = {row["category_id"] for row in categories_rows if row["category_id"]}
    missing_name_count = sum(1 for row in products_rows if not row["name"])
    missing_category_ref_count = sum(
        1 for row in products_rows if row["category_id"] and row["category_id"] not in category_ids
    )
    price_offer_ids = {row["offer_id"] for row in prices_rows}
    missing_products_for_prices = sorted(price_offer_ids - offer_ids)

    sample_size = min(10, len(products_rows))
    sample = random.sample(products_rows, sample_size) if sample_size else []

    print(f"categories: {len(categories_rows)}")
    print(f"offers_in_xml: {len(offers_node.findall('offer'))}")
    print(f"products_rows: {len(products_rows)}")
    print(f"prices_rows: {len(prices_rows)}")
    print(f"media_rows: {len(media_rows)}")
    print(f"params_rows: {len(params_rows)}")
    print(f"duplicate_offer_ids: {len(duplicate_offer_ids)}")
    print(f"missing_name_count: {missing_name_count}")
    print(f"missing_category_ref_count: {missing_category_ref_count}")
    print(f"missing_products_for_prices_count: {len(missing_products_for_prices)}")
    print("sample_products:")
    for row in sample:
        print(
            f"- {row['offer_id']} | {row['name'][:80]} | category={row['category_id']}"
        )


if __name__ == "__main__":
    main()
