"""Idempotent car catalog population used by seed_demo."""

from .models import CarMake, CarModel


def initiate():
    catalog = {
        "Nissan": [("Pathfinder", "SUV"), ("Qashqai", "SUV"), ("X-Trail", "SUV")],
        "Mercedes-Benz": [("A-Class", "SEDAN"), ("C-Class", "SEDAN"), ("E-Class", "SEDAN")],
        "Audi": [("A4", "SEDAN"), ("A5", "COUPE"), ("A6", "SEDAN")],
        "Kia": [("Sorento", "SUV"), ("Carnival", "MINIVAN"), ("Cerato", "SEDAN")],
        "Toyota": [("Corolla", "SEDAN"), ("Camry", "SEDAN"), ("Kluger", "SUV")],
    }
    for name, models in catalog.items():
        make, _ = CarMake.objects.get_or_create(name=name, defaults={"description": f"{name} vehicles"})
        for model_name, car_type in models:
            CarModel.objects.get_or_create(car_make=make, name=model_name, year=2023, defaults={"type": car_type})
