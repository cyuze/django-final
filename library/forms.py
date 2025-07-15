from django import forms    # Djangoのformsモジュールをインポート

# SearchFormクラスを定義
class SearchForm(forms.Form):
    words = forms.CharField(
        label='', 
        max_length=50, 
        widget=forms.TextInput(attrs={
            'class':'form-control me-2', 
            'placeholder':'キーワードを入力', 
        })
    )