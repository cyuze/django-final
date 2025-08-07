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
    path('<int:pk>/rent', views.rent_book, name="rentMethod"),     # 本を借りるメソッド
    path('<int:pk>/return', views.return_book, name="returnMethod"),     # 本を返すメソッド
    path('<int:pk>/rented', views.rent, name="rentPage"),     # 本を借りた後のリダイレクトページ
    path('<int:pk>/can_return_book', views.can_return_book, name="can_return_book"),     # 返すべき本かどうかの判定関数
    path('rental_history/', views.RentalHistoryView.as_view(), name='rental_history'),      # ログインユーザーが借りている本の一覧表示
    path('return_history/', views.ReturnHistoryView.as_view(), name='return_history'),      # ログインユーザーが返した本の一覧表示
    path('auth_rental_history/', views.AuthRentalHistoryView.as_view(), name='auth_rental_history'),      # 管理者権限ログインユーザーが借りている本の一覧表示
    path('auth_return_history/', views.AuthReturnHistoryView.as_view(), name='auth_return_history'),      # 管理者権限ログインユーザーが返した本の一覧表示
    path('<int:pk>/post_review', views.post_review, name="post_review"),     # レビューをポストするメソッド
]