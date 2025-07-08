from django.contrib import admin
from .models import Book, LendingHistory

admin.site.register(Book)
admin.site.register(LendingHistory)

# Register your models here.
