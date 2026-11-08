"""Persistent data for the standalone capstone deployment."""

from datetime import date

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CarMake(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name="models")
    name = models.CharField(max_length=50)
    CAR_TYPES = [
        ("SEDAN", "Sedan"),
        ("SUV", "SUV"),
        ("WAGON", "Wagon"),
        ("HATCHBACK", "Hatchback"),
        ("COUPE", "Coupe"),
        ("MINIVAN", "Minivan"),
        ("CONVERTIBLE", "Convertible"),
        ("PICKUP", "Pickup"),
    ]
    type = models.CharField(max_length=20, choices=CAR_TYPES, default="SUV")
    year = models.IntegerField(
        default=2023, validators=[MinValueValidator(1900), MaxValueValidator(date.today().year + 1)]
    )

    class Meta:
        constraints = [models.UniqueConstraint(fields=["car_make", "name", "year"], name="unique_car_model_year")]

    def __str__(self):
        return f"{self.car_make} {self.name} ({self.year})"


class Dealer(models.Model):
    full_name = models.CharField(max_length=160)
    short_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    st = models.CharField(max_length=2)
    address = models.CharField(max_length=200)
    zip = models.CharField(max_length=12)
    lat = models.FloatField(default=0)
    long = models.FloatField(default=0)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.full_name


class Review(models.Model):
    dealership = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=160)
    review = models.TextField(max_length=5000)
    purchase = models.BooleanField(default=False)
    purchase_date = models.DateField(null=True, blank=True)
    car_make = models.CharField(max_length=100, blank=True)
    car_model = models.CharField(max_length=100, blank=True)
    car_year = models.PositiveIntegerField(null=True, blank=True)
    sentiment = models.CharField(max_length=10, default="neutral")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.name}: {self.dealership}"
