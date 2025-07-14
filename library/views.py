from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import Book
from django.urls import reverse_lazy    # reverse_lazy関数をインポート

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