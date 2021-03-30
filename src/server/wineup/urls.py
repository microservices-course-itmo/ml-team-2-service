from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.user_list),
    path("wines/", views.wine_list),
    path("review/", views.review_list),
    path("print/", views.print_matrix),
    path("recommendations/<int:user_id>/", views.get_recommendations),
    path("user_sync/", views.user_sync),
    path("catalog_sync/", views.catalog_sync),
    path("favorites_sync/", views.favorites_sync),
    # path('wine/<int:pk>/', views.wine_detail),
]
