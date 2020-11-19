from django.contrib import admin
from .models import Wine, User, Review

# Register your models here.
admin.site.register(Wine)
admin.site.register(User)
admin.site.register(Review)
