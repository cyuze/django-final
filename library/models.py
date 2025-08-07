from django.db import models
from django.contrib.auth.models import User  # ユーザー管理
from django.urls import reverse # reverse関数をインポート

class Book(models.Model):
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    ISBN = models.CharField(max_length=20)
    author = models.CharField(max_length=20)
    publisher = models.CharField(max_length=20)
    content = models.TextField()
    lendStatus = models.BooleanField(default=True)  # True = 貸出可能

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("library:detail", kwargs={"pk": self.pk})
    
class LendingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rentalDate = models.DateField(auto_now_add=True)
    returnDate = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user}, {self.book}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    postDate = models.DateField(auto_now_add=True)
    star = models.CharField(max_length=20, blank=True, null=True)
    content = models.TextField()

    def __str__(self):
        return f"{self.user}, {self.book}"
