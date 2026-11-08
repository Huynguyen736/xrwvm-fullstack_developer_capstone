from django.contrib import admin

from .models import CarMake, CarModel, Dealer, Review


class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 0


@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    inlines = [CarModelInline]


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ("name", "car_make", "type", "year")
    list_filter = ("car_make", "type")


@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "city", "state")
    list_filter = ("state",)
    search_fields = ("full_name", "city")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "dealership", "sentiment", "purchase", "created_at")
    list_filter = ("sentiment", "purchase")
    readonly_fields = ("created_at",)
