from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import Book
from .models import LendingHistory
from django.db.models import Q
from django.urls import reverse_lazy    # reverse_lazy関数をインポート
from .forms import SearchForm       # forms.pyからsearchFormクラスをインポート

class IndexView(generic.ListView):
    model = Book
    template_name = 'library/index.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        books = context['object_list']

        # ログインユーザーが借りている本のID一覧
        user_lending_ids = set()
        if user.is_authenticated:
            user_lending_ids = set(
                LendingHistory.objects.filter(user=user, returnDate__isnull=True)
                .values_list('book__id', flat=True)
            )

        # 各Bookオブジェクトに貸出ユーザー一覧と「自分が借りているか」フラグを追加
        lending_info = LendingHistory.objects.filter(returnDate__isnull=True)
        lending_map = {}
        for entry in lending_info:
            lending_map.setdefault(entry.book_id, []).append(entry.user.username)

        for book in books:
            book.lending_users = lending_map.get(book.id, [])
            book.is_borrowed_by_user = user.username in book.lending_users if user.is_authenticated else False

        context['user'] = user  # テンプレートで使うために明示的に渡す
        return context

class DetailView(generic.DetailView):
    model = Book
    template_name = 'library/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        book = self.object
        context['can_return'] = LendingHistory.objects.filter(
            user=user,
            book=book,
            returnDate__isnull=True
        ).exists() if user.is_authenticated else False
        
        # 貸出中の全ユーザー（この本を借りていて、まだ返却していない人）
        lending_users = LendingHistory.objects.filter(
            book=book,
            returnDate__isnull=True
        ).values_list('user__username', flat=True)

        context['lending_users'] = lending_users
        
        context['reviews'] = Review.objects.filter(book=book).order_by('-postDate')

        return context
    
    
    
class CreateView(generic.CreateView):
    model = Book
    template_name = 'library/create.html'
    fields = '__all__'
    
class UpdateView(generic.UpdateView):
    model = Book
    template_name = 'library/create.html'
    fields = ['title', 'genre', 'ISBN', 'author', 'publisher', 'content']  # lendStatusを含めない

    def form_valid(self, form):
        # lendStatusの値を元のインスタンスからコピー
        form.instance.lendStatus = self.get_object().lendStatus
        return super().form_valid(form)
    
class DeleteView(generic.DeleteView):
    model = Book
    template_name = 'library/delete.html'
    success_url = reverse_lazy('library:index')
    
# 検索機能のビュー
def search(request):
    articles = Book.objects.none()
    searchform = SearchForm(request.GET)
    if searchform.is_valid():
        query = searchform.cleaned_data['words']
        articles = Book.objects.filter(
            Q(title__icontains=query) |
            Q(genre__icontains=query) |
            Q(author__icontains=query) |
            Q(publisher__icontains=query) |
            Q(content__icontains=query) |
            Q(ISBN__icontains=query)
        )
    return render(request, 'library/results.html', {
        'articles': articles,
        'object_list': articles,
        'searchform': searchform
    })
        
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404

@login_required
def rent_book(request, pk):
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=pk)
        user = request.user
        if book.lendStatus:
            LendingHistory.objects.create(user=user, book=book)
            book.lendStatus = False
            book.save()
        return redirect('library:detail', pk=pk)
    else:
        return redirect('library:rentPage', pk=pk)

def rent(request, pk):
    book = get_object_or_404(Book, pk=pk)
    mode = request.GET.get('mode', 'rent')
    return render(request, 'library/rent.html', {'object': book, 'mode': mode})

def can_return_book(user, pk):
    return LendingHistory.objects.filter(
        user=user,
        book=pk,
        returnDate__isnull=True
    ).exists()
    
from django.utils import timezone

@login_required
def return_book(request, pk):
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=pk)
        user = request.user
        # 該当履歴を取得
        history = LendingHistory.objects.filter(user=user, book=book, returnDate__isnull=True).first()
        if history:
            history.returnDate = timezone.now().date()
            history.save()
            book.lendStatus = True
            book.save()
        return redirect('library:detail', pk=pk)
    else:
        return redirect('library:rentPage', pk=pk)
    
from django.db.models import Q

class RentalHistoryView(generic.ListView):
    model = LendingHistory
    template_name = 'library/rental_history.html'
    context_object_name = 'histories'

    def get_queryset(self):
        return LendingHistory.objects.filter(
            Q(user=self.request.user) & Q(returnDate__isnull=True)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context['user_lending_ids'] = [
                rental.book.id for rental in LendingHistory.objects.filter(user=user)
            ]
        else:
            context['user_lending_ids'] = []
        return context
    
class ReturnHistoryView(generic.ListView):
    model = LendingHistory
    template_name = 'library/return_history.html'
    context_object_name = 'histories'

    def get_queryset(self):
        return LendingHistory.objects.filter(
            Q(user=self.request.user) & Q(returnDate__isnull=False)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context['user_lending_ids'] = [
                rental.book.id for rental in LendingHistory.objects.filter(user=user)
            ]
        else:
            context['user_lending_ids'] = []
        return context
    

class AuthRentalHistoryView(generic.ListView):
    model = LendingHistory
    template_name = 'library/auth_rental_history.html'
    context_object_name = 'histories'

    def get_queryset(self):
        return LendingHistory.objects.filter(
            Q(returnDate__isnull=True)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_lending_ids'] = [
            rental.book.id for rental in LendingHistory.objects.filter(user=user)
        ]
        return context
    
class AuthReturnHistoryView(generic.ListView):
    model = LendingHistory
    template_name = 'library/auth_return_history.html'
    context_object_name = 'histories'

    def get_queryset(self):
        return LendingHistory.objects.all()
    
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Review, Book

@login_required
def post_review(request, pk):
    user = request.user
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        star = request.POST.get("star")
        content = request.POST.get("review")

        if star and content:
            Review.objects.create(
                user=user,
                book=book,
                star=star,
                content=content
            )
            return redirect("library:detail", pk=pk)  # 遷移先はお好みに応じて調整
        else:
            return render(request, "library:detail", {
                "book": book,
                "error": "評価とレビュー内容は必須です。",
            })

    return redirect("library:detail", pk=pk)



    
