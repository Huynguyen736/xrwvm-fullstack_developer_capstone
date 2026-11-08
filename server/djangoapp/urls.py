from django.urls import path

from . import views

app_name = "djangoapp"
urlpatterns = [
    path("session", views.session, name="session"),
    path("register", views.registration, name="register"),
    path("login", views.login_user, name="login"),
    path("logout/", views.logout_request, name="logout"),
    path("get_cars", views.get_cars, name="getcars"),
    path("get_dealers/", views.get_dealerships, name="get_dealers"),
    path("get_dealers/<str:state>", views.get_dealerships, name="get_dealers_by_state"),
    path("dealer/<int:dealer_id>", views.get_dealer_details, name="dealer_details"),
    path("reviews/dealer/<int:dealer_id>", views.get_dealer_reviews, name="dealer_reviews"),
    path("add_review", views.add_review, name="add_review"),
    path("analyze/<path:text>", views.analyze_review, name="analyze_review"),
    path("health", views.health, name="health"),
]
