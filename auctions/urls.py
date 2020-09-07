from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-listing", views.CreateListing, name="create_listing"),
    path("view-listing/<int:productid>",views.ViewListing,name="view_listing"),
    path("watchlist",views.Watchlist,name="watchlist"),
    path("categories",views.Categories,name="categories")
]
