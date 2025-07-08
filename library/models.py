from django.db import models
from django.contrib.auth.models import User  # ユーザー管理

class Book(models.Model):
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    ISBN = models.CharField(max_length=20)
    author = models.CharField(max_length=20)
    publisher = models.CharField(max_length=20)
    content = models.TextField()
    lendStatus = models.BooleanField(default=True)  # True = 貸出可能

    def __str__(self):
        return self.title, self.genre, self.ISBN, self.content, self.lendStatus    
    
class LendingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rentalDate = models.DateField(auto_now_add=True)
    returnDate = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.user, self.book, self.rentalDate, self.returnDate