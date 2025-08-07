from django.contrib import admin
from .models import Book, LendingHistory, Review

admin.site.register(Book)
admin.site.register(LendingHistory)
admin.site.register(Review)

# Register your models here.
