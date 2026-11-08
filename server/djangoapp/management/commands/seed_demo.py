"""Load the upstream educational sample dataset without replacing user data."""

import json
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from djangoapp.models import Dealer, Review
from djangoapp.populate import initiate
from djangoapp.sentiment import analyze


class Command(BaseCommand):
    help = "Seed demo dealers, reviews, and cars; existing records are preserved."

    @transaction.atomic
    def handle(self, *args, **options):
        data_dir = settings.BASE_DIR / "database" / "data"
        dealers = json.loads((data_dir / "dealerships.json").read_text(encoding="utf-8"))["dealerships"]
        reviews = json.loads((data_dir / "reviews.json").read_text(encoding="utf-8"))["reviews"]
        for item in dealers:
            item = dict(item)
            dealer_id = item.pop("id")
            Dealer.objects.get_or_create(pk=dealer_id, defaults=item)
        # Seed only an empty review table. Explicit upstream IDs must never
        # collide with a user's review after subsequent restarts.
        if not Review.objects.exists():
            for item in reviews:
                item = dict(item)
                review_id = item.pop("id")
                dealer_id = item.pop("dealership")
                if not Dealer.objects.filter(pk=dealer_id).exists():
                    continue
                value = item.get("purchase_date")
                item["purchase_date"] = datetime.strptime(value, "%m/%d/%Y").date() if value else None
                Review.objects.create(pk=review_id, dealership_id=dealer_id, sentiment=analyze(item["review"]), **item)
        initiate()
        self.stdout.write(
            self.style.SUCCESS(f"Demo data ready: {Dealer.objects.count()} dealers, {Review.objects.count()} reviews.")
        )
