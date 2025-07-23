from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(City)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(StarclinchBaseUser)
admin.site.register(Recipe)
admin.site.register(Rating)