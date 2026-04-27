"""Import product data from CSV files exported from prom.xml."""

from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalog.models import Category, Product, ProductImage, ProductParam, WholesalePrice


class Command(BaseCommand):
    help = "Import categories, products, prices, media, params from CSV files in output/"

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            type=str,
            default=str(settings.CSV_DATA_DIR),
            help="Path to directory containing CSV files",
        )

    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"])
        self._import_categories(data_dir / "categories.csv")
        self._import_products(data_dir / "products.csv")
        self._import_prices(data_dir / "prices.csv")
        self._import_media(data_dir / "media.csv")
        self._import_params(data_dir / "params.csv")
        self._generate_wholesale_prices()
        self.stdout.write(self.style.SUCCESS("Import complete."))

    def _read_csv(self, path: Path) -> list[dict[str, str]]:
        with path.open(encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def _import_categories(self, path: Path) -> None:
        rows = self._read_csv(path)
        self.stdout.write(f"Importing {len(rows)} categories...")

        cat_map: dict[str, Category] = {}
        for row in rows:
            cat, _ = Category.objects.update_or_create(
                original_id=row["category_id"],
                defaults={"name": row["category_name"]},
            )
            cat_map[row["category_id"]] = cat

        Category.objects.update(parent=None, lft=0, rght=0, tree_id=0, level=0)

        for row in rows:
            pid = row["parent_id"]
            if pid and pid in cat_map:
                Category.objects.filter(pk=cat_map[row["category_id"]].pk).update(
                    parent=cat_map[pid]
                )

        Category.objects.rebuild()
        self.stdout.write(self.style.SUCCESS(f"  {len(cat_map)} categories imported."))

    def _import_products(self, path: Path) -> None:
        rows = self._read_csv(path)
        self.stdout.write(f"Importing {len(rows)} products...")

        cat_lookup = {c.original_id: c for c in Category.objects.all()}
        created = 0
        for row in rows:
            category = cat_lookup.get(row["category_id"])
            slug = slugify(row["name"][:200], allow_unicode=True) or "product"
            if Product.objects.filter(slug=slug).exclude(offer_id=row["offer_id"]).exists():
                slug = f"{slug}-{row['offer_id'].lower()}"

            _, was_created = Product.objects.update_or_create(
                offer_id=row["offer_id"],
                defaults={
                    "sku": row.get("sku", ""),
                    "name": row["name"],
                    "slug": slug,
                    "category": category,
                    "brand": row.get("brand", ""),
                    "description": row.get("description", ""),
                },
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"  {created} new, {len(rows) - created} updated."))

    def _import_prices(self, path: Path) -> None:
        rows = self._read_csv(path)
        self.stdout.write(f"Importing {len(rows)} prices...")

        updated = 0
        for row in rows:
            try:
                price = Decimal(row["price"])
            except (InvalidOperation, ValueError):
                continue

            old_price = None
            if row.get("old_price"):
                try:
                    old_price = Decimal(row["old_price"])
                except (InvalidOperation, ValueError):
                    pass

            count = Product.objects.filter(offer_id=row["offer_id"]).update(
                retail_price=price,
                old_price=old_price,
                currency=row.get("currency", "UAH"),
                is_available=row.get("availability", "").lower() == "true",
            )
            updated += count

        self.stdout.write(self.style.SUCCESS(f"  {updated} prices updated."))

    def _import_media(self, path: Path) -> None:
        rows = self._read_csv(path)
        self.stdout.write(f"Importing {len(rows)} images...")

        product_cache = {p.offer_id: p for p in Product.objects.only("id", "offer_id")}
        bulk = []
        seen = set()
        for row in rows:
            product = product_cache.get(row["offer_id"])
            if not product:
                continue
            key = (product.id, row["image_url"])
            if key in seen:
                continue
            seen.add(key)
            bulk.append(
                ProductImage(
                    product=product,
                    image_url=row["image_url"],
                    sort_order=int(row.get("image_order", 0)),
                )
            )

        ProductImage.objects.all().delete()
        ProductImage.objects.bulk_create(bulk, batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"  {len(bulk)} images imported."))

    def _import_params(self, path: Path) -> None:
        rows = self._read_csv(path)
        self.stdout.write(f"Importing {len(rows)} params...")

        product_cache = {p.offer_id: p for p in Product.objects.only("id", "offer_id")}
        bulk = []
        box_qty_updates: dict[int, int] = {}

        for row in rows:
            product = product_cache.get(row["offer_id"])
            if not product:
                continue
            bulk.append(
                ProductParam(product=product, name=row["param_name"], value=row["param_value"])
            )
            if row["param_name"] == "Количество в ящике":
                try:
                    box_qty_updates[product.id] = int(row["param_value"])
                except (ValueError, TypeError):
                    pass

        ProductParam.objects.all().delete()
        ProductParam.objects.bulk_create(bulk, batch_size=1000)

        for pid, qty in box_qty_updates.items():
            Product.objects.filter(id=pid).update(box_quantity=qty)

        self.stdout.write(
            self.style.SUCCESS(f"  {len(bulk)} params, {len(box_qty_updates)} box quantities.")
        )

    def _generate_wholesale_prices(self) -> None:
        """Auto-generate wholesale prices: ~20% discount at box_quantity threshold."""
        products = Product.objects.filter(box_quantity__gt=0, retail_price__gt=0)
        self.stdout.write(f"Generating wholesale prices for {products.count()} products...")

        bulk = []
        for p in products.iterator():
            wholesale = (p.retail_price * Decimal("0.80")).quantize(Decimal("0.01"))
            bulk.append(WholesalePrice(product=p, min_quantity=p.box_quantity, price=wholesale))

        WholesalePrice.objects.all().delete()
        WholesalePrice.objects.bulk_create(bulk, batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"  {len(bulk)} wholesale prices generated."))
