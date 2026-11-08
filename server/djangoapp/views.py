"""Same-origin JSON API backed by Django sessions and persistent models."""

import json
from datetime import date
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET, require_POST

from .models import CarMake, CarModel, Dealer, Review
from .sentiment import analyze


def error(message, status=400):
    return JsonResponse({"status": status, "error": message}, status=status)


def json_body(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            if not isinstance(data, dict):
                return error("The request body must be a JSON object.")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return error("Invalid JSON request body.")
        return view(request, data, *args, **kwargs)

    return wrapped


def user_details(request):
    user = request.user
    return {
        "authenticated": user.is_authenticated,
        "userName": user.username if user.is_authenticated else "",
        "firstName": user.first_name if user.is_authenticated else "",
        "lastName": user.last_name if user.is_authenticated else "",
        "email": user.email if user.is_authenticated else "",
        "csrfToken": get_token(request),
    }


@require_GET
def session(request):
    return JsonResponse(user_details(request))


@require_POST
@json_body
def login_user(request, data):
    username, password = data.get("userName"), data.get("password")
    if not isinstance(username, str) or not isinstance(password, str) or not username or not password:
        return error("Username and password are required.")
    user = authenticate(request, username=username, password=password)
    if user is None:
        return error("Invalid username or password.", 401)
    login(request, user)
    return JsonResponse({"status": "Authenticated", **user_details(request)})


@require_POST
def logout_request(request):
    logout(request)
    return JsonResponse({"success": True, "message": "Logged out successfully", **user_details(request)})


@require_POST
@json_body
def registration(request, data):
    fields = ("userName", "firstName", "lastName", "email", "password")
    if any(not isinstance(data.get(field), str) or not data[field].strip() for field in fields):
        return error("Username, first name, last name, email and password are required.")
    username = data["userName"].strip()
    first_name, last_name, email = data["firstName"].strip(), data["lastName"].strip(), data["email"].strip()
    if len(username) > 150 or len(first_name) > 150 or len(last_name) > 150 or len(email) > 254:
        return error("An account field exceeds its maximum length.")
    user = User(username=username, first_name=first_name, last_name=last_name, email=email)
    try:
        User._meta.get_field("username").run_validators(username)
        validate_email(email)
        validate_password(data["password"], user=user)
    except ValidationError as exc:
        return error(" ".join(exc.messages))
    if User.objects.filter(username=username).exists():
        return error("This username is already registered.", 409)
    try:
        user.set_password(data["password"])
        user.save()
    except IntegrityError:
        return error("This username is already registered.", 409)
    login(request, user)
    return JsonResponse({"status": "Authenticated", **user_details(request)}, status=201)


@require_GET
def get_cars(request):
    cars = [
        {"CarMake": car.car_make.name, "CarModel": car.name, "type": car.type, "year": car.year}
        for car in CarModel.objects.select_related("car_make").order_by("car_make__name", "name")
    ]
    makes = list(CarMake.objects.order_by("name").values("id", "name", "description"))
    return JsonResponse({"status": 200, "CarMakes": makes, "CarModels": cars})


@require_GET
def get_dealerships(request, state="All"):
    dealers = Dealer.objects.all()
    if state.lower() != "all":
        dealers = dealers.filter(state__iexact=state)
    return JsonResponse({"status": 200, "dealers": list(dealers.values())})


@require_GET
def get_dealer_details(request, dealer_id):
    dealer = list(Dealer.objects.filter(pk=dealer_id).values())
    if not dealer:
        return error("Dealer not found.", 404)
    return JsonResponse({"status": 200, "dealer": dealer})


def serialize_review(review):
    return {
        "id": review.pk,
        "name": review.name,
        "dealership": review.dealership_id,
        "review": review.review,
        "purchase": review.purchase,
        "purchase_date": review.purchase_date.isoformat() if review.purchase_date else "",
        "car_make": review.car_make,
        "car_model": review.car_model,
        "car_year": review.car_year,
        "sentiment": review.sentiment,
        "created_at": review.created_at.isoformat(),
    }


@require_GET
def get_dealer_reviews(request, dealer_id):
    if not Dealer.objects.filter(pk=dealer_id).exists():
        return error("Dealer not found.", 404)
    reviews = [serialize_review(review) for review in Review.objects.filter(dealership_id=dealer_id)]
    return JsonResponse({"status": 200, "reviews": reviews})


@require_POST
@json_body
def add_review(request, data):
    if not request.user.is_authenticated:
        return error("Please log in to post a review.", 403)
    dealer_id = data.get("dealership")
    if isinstance(dealer_id, bool) or not isinstance(dealer_id, (int, str)):
        return error("A valid dealership ID is required.")
    try:
        dealer = Dealer.objects.get(pk=int(dealer_id))
    except (ValueError, TypeError, Dealer.DoesNotExist):
        return error("Dealer not found.", 404)
    text = data.get("review")
    if not isinstance(text, str) or not text.strip() or len(text) > 5000:
        return error("Review must contain between 1 and 5000 characters.")
    purchase = data.get("purchase", False)
    if not isinstance(purchase, bool):
        return error("Purchase must be true or false.")
    details = {}
    if purchase:
        make, model = data.get("car_make"), data.get("car_model")
        if (
            not isinstance(make, str)
            or not isinstance(model, str)
            or not make.strip()
            or not model.strip()
            or len(make) > 100
            or len(model) > 100
        ):
            return error("A valid car make and model are required for a purchase.")
        try:
            purchase_date = date.fromisoformat(data.get("purchase_date", ""))
            car_year_value = data.get("car_year")
            if isinstance(car_year_value, bool) or isinstance(car_year_value, float):
                raise ValueError
            car_year = int(car_year_value)
        except (TypeError, ValueError):
            return error("A valid purchase date and car year are required.")
        if purchase_date > date.today() or not 1900 <= car_year <= date.today().year + 1:
            return error("Purchase date cannot be in the future; car year must be valid.")
        details = {
            "purchase_date": purchase_date,
            "car_year": car_year,
            "car_make": make.strip(),
            "car_model": model.strip(),
        }
    review = Review.objects.create(
        dealership=dealer,
        author=request.user,
        name=request.user.get_full_name().strip() or request.user.username,
        review=text.strip(),
        purchase=purchase,
        sentiment=analyze(text),
        **details,
    )
    return JsonResponse(
        {"status": 200, "message": "Review posted successfully", "review": serialize_review(review)}, status=201
    )


@require_GET
def analyze_review(request, text):
    if len(text) > 5000:
        return error("Review text cannot exceed 5000 characters.")
    return JsonResponse({"text": text, "sentiment": analyze(text), "method": "local lexicon baseline"})


@require_GET
def health(request):
    return JsonResponse({"status": "ok", "dealers": Dealer.objects.count()})
