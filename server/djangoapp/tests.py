"""Regression tests for the self-contained dealership API."""

import json

from django.contrib.auth.models import User
from django.test import Client, TestCase

from .models import Dealer, Review


class DealershipAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dealer = Dealer.objects.create(
            id=1,
            full_name="Kansas Cars",
            short_name="Kansas",
            state="Kansas",
            st="KS",
            city="Wichita",
            address="1 Main Street",
            zip="67201",
        )
        Dealer.objects.create(
            id=2,
            full_name="Texas Cars",
            short_name="Texas",
            state="Texas",
            st="TX",
            city="Austin",
            address="2 Main Street",
            zip="78701",
        )
        cls.user = User.objects.create_user(
            "reviewer", "reviewer@example.com", "A-test-password-249!", first_name="Huy", last_name="Nguyen"
        )

    def post_json(self, path, payload, client=None, token=None):
        headers = {"HTTP_X_CSRFTOKEN": token} if token else {}
        return (client or self.client).post(path, json.dumps(payload), content_type="application/json", **headers)

    def test_filter_only_returns_requested_state(self):
        response = self.client.get("/djangoapp/get_dealers/Kansas")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([d["id"] for d in response.json()["dealers"]], [1])

    def test_missing_dealer_returns_404(self):
        self.assertEqual(self.client.get("/djangoapp/dealer/999").status_code, 404)

    def test_session_csrf_and_login_logout(self):
        client = Client(enforce_csrf_checks=True)
        session = client.get("/djangoapp/session").json()
        self.assertFalse(session["authenticated"])
        payload = {"userName": "reviewer", "password": "A-test-password-249!"}
        self.assertEqual(self.post_json("/djangoapp/login", payload, client).status_code, 403)
        self.assertEqual(self.post_json("/djangoapp/login", payload, client, session["csrfToken"]).status_code, 200)
        session = client.get("/djangoapp/session").json()
        self.assertTrue(session["authenticated"])
        self.assertEqual(session["userName"], "reviewer")
        self.assertEqual(self.post_json("/djangoapp/logout/", {}, client, session["csrfToken"]).status_code, 200)
        self.assertFalse(client.get("/djangoapp/session").json()["authenticated"])

    def test_login_rejects_invalid_credentials_and_bad_json(self):
        self.assertEqual(
            self.post_json("/djangoapp/login", {"userName": "reviewer", "password": "bad"}).status_code, 401
        )
        self.assertEqual(self.client.post("/djangoapp/login", "{", content_type="application/json").status_code, 400)
        self.assertEqual(self.client.get("/djangoapp/login").status_code, 405)

    def test_registration_requires_all_five_fields_and_validates(self):
        self.assertEqual(self.post_json("/djangoapp/register", {"userName": "new"}).status_code, 400)
        payload = {
            "userName": "newreviewer",
            "firstName": "New",
            "lastName": "Reviewer",
            "email": "new@example.com",
            "password": "My-test-password-249!",
        }
        self.assertEqual(self.post_json("/djangoapp/register", payload).status_code, 201)
        self.assertTrue(self.client.get("/djangoapp/session").json()["authenticated"])
        self.assertEqual(self.post_json("/djangoapp/register", payload).status_code, 409)

    def test_review_requires_login_and_uses_server_side_identity(self):
        payload = {"dealership": 1, "review": "Fantastic services", "purchase": False, "name": "Forged identity"}
        self.assertEqual(self.post_json("/djangoapp/add_review", payload).status_code, 403)
        self.client.force_login(self.user)
        response = self.post_json("/djangoapp/add_review", payload)
        self.assertEqual(response.status_code, 201)
        review = Review.objects.get()
        self.assertEqual(review.name, "Huy Nguyen")
        self.assertEqual(review.author, self.user)
        self.assertEqual(review.sentiment, "positive")
        reviews = self.client.get("/djangoapp/reviews/dealer/1").json()["reviews"]
        self.assertEqual(reviews[0]["review"], payload["review"])

    def test_purchase_details_are_validated(self):
        self.client.force_login(self.user)
        payload = {"dealership": 1, "review": "Great dealer", "purchase": True}
        self.assertEqual(self.post_json("/djangoapp/add_review", payload).status_code, 400)
        payload.update(purchase_date="2099-01-01", car_make="Toyota", car_model="Camry", car_year=2023)
        self.assertEqual(self.post_json("/djangoapp/add_review", payload).status_code, 400)
        payload["purchase_date"] = "2025-01-01"
        self.assertEqual(self.post_json("/djangoapp/add_review", payload).status_code, 201)

    def test_sentiment_labels_and_negation(self):
        cases = {
            "Fantastic services": "positive",
            "Terrible experience": "negative",
            "The dealership is in Kansas": "neutral",
            "not good": "negative",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(self.client.get("/djangoapp/analyze/" + text).json()["sentiment"], expected)


class DemoSeedTests(TestCase):
    def test_seed_is_idempotent_and_preserves_user_reviews(self):
        from io import StringIO

        from django.core.management import call_command

        from .models import CarMake, CarModel

        call_command("seed_demo", stdout=StringIO())
        counts = (Dealer.objects.count(), Review.objects.count(), CarMake.objects.count(), CarModel.objects.count())
        self.assertGreater(counts[0], 0)
        self.assertGreater(Dealer.objects.filter(state="Kansas").count(), 0)
        review = Review.objects.first()
        review.review = "User edited review"
        review.save()
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(
            counts, (Dealer.objects.count(), Review.objects.count(), CarMake.objects.count(), CarModel.objects.count())
        )
        review.refresh_from_db()
        self.assertEqual(review.review, "User edited review")
