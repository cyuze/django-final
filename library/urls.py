from django.urls import path, include
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.IndexView.as_view() , name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),   # 投稿詳細ページ
    path('create/', views.CreateView.as_view(), name='create'),     # 新規投稿ページ
    path('<int:pk>/update/', views.UpdateView.as_view(), name="update"),  # 投稿編集ページ
    path('<int:pk>/delete/', views.DeleteView.as_view(), name="delete"),  # 投稿削除ページ
    path('search/', views.search, name='search'),    # 検索
    path('accounts/', include('django.contrib.auth.urls')),     # ユーザー認証用のビューを呼び出す
    path('<int:pk>/rent', views.rent_book, name="rent"),     # 本を借りる
]