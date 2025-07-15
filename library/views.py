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
    book = get_object_or_404(Book, pk=pk)
    user = request.user
    LendingHistory.objects.create(user=user, book=book)
    return redirect('library:detail', pk=pk)