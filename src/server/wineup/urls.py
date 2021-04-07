import os
from django.urls import path
from . import views

path_prefix = os.environ.get("METHODS_PATH_PREFIX", "")

urlpatterns = [
    path("users/", views.user_list),
    path("wines/", views.wine_list),
    path("review/", views.review_list),
    path("print/", views.print_matrix),
    path(f"{path_prefix}recommendations/<int:user_id>/", views.get_recommendations),
    path(f"{path_prefix}recommendations/", views.get_recommendations_default),
    path("user_sync/", views.user_sync),
    path("catalog_sync/", views.catalog_sync),
    path("favorites_sync/", views.favorites_sync),
]
