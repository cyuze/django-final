from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import Book
from .models import LendingHistory
from django.db.models import Q
from django.urls import reverse_lazy    # reverse_lazy関数をインポート
from .forms import SearchForm       # forms.pyからsearchFormクラスをインポート

class IndexView(generic.ListView):
    model = Book     #Bookモデルを使用 
    template_name = 'library/index.html'    # 使用するテンプレート名を指定（Articleも自動で渡す）

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
    
class RentalHistoryView(generic.ListView):
    model = LendingHistory
    template_name = 'library/rental_history.html'
    context_object_name = 'histories'

    def get_queryset(self):
        return LendingHistory.objects.filter(user=self.request.user)