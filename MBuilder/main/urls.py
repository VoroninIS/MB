from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("schem_generation", views.schem_generation),
    path("about", views.about),
    path("faq", views.faq),
    path("price", views.price),
    path("support", views.support),
    path("cookies", views.cookies),
    path("terms", views.terms),
    path("privacy", views.privacy),
]
