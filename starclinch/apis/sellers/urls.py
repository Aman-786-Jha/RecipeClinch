from django.urls import path 
from .views import *
from . import views 

urlpatterns = [

    ######################### Seller Authentication ############################
    path('seller/signup/',SellerSignupView.as_view(),name='seller_signup'),
    path('seller/login/',SellerLoginView.as_view(),name='seller_login'),
    path('seller/logout/',SellerUserLogoutView.as_view(),name='seller_logout'),

    ################################ Seller Recipe #######################

    path("seller/recipe/create/", RecipeCreateView.as_view(), name="seller-recipe-create"),
    path("seller/recipe/list/", SellerRecipeListView.as_view(), name="seller-recipe-list"),
    path('seller/recipe/<uuid:id>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('seller/update-recipe/<uuid:recipe_id>/', RecipeUpdateAPIView.as_view(), name='update-recipe'),
    path('seller/recipe/delete/<uuid:recipe_id>/', RecipeDeleteAPIView.as_view(), name='delete-recipe'),
]
