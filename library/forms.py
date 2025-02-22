from django import forms 
from  .models import Category, Book

class AddBookForm(forms.ModelForm):

    category = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), label="Категории", required=False)

    class Meta:
        model = Book 
        fields = ['title', 'author', 'content', 'isbn', 'publisher','category', 'copies_available', 'photo', 'slug']