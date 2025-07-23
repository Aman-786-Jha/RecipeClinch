from django.urls import path 
from .views import *
from . import views 

urlpatterns = [

    ######################## Authentication #############################
    path('customer/signup/',CustomerSignupView.as_view(),name='customer_signup'),
    path('customer/login/',CustomerLoginView.as_view(),name='customer_login'),
    path('customer/logout/',CustomerUserLogoutView.as_view(),name='customer_logout'),

    ################################ Recipe Apis ###########################

    path("customer/recipe/list/", CustomerRecipeListView.as_view(), name="customer-recipe-list"),
    path('customer/recipe/detail/<uuid:id>/', RecipeDetailCustomerView.as_view(), name='customer-recipe-detail'),
    path("customer/recipes/<uuid:id>/rate/", RateRecipeAPIView.as_view(), name="rate-recipe"),
    path("customer/recipes/ratelist/", CustomerRatingListView.as_view(), name="ratelist-recipe"),

    
]
