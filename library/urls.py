from django.urls import path
from . import views 


urlpatterns = [
    path('', views.home, name='home'),
    path('addbook/', views.AddBook.as_view(), name='add_book'),
    path('editbook/<slug:slug>/', views.UpdatePage.as_view(), name='edit_book'),
    path('book/<slug:book_slug>/', views.BookDetail.as_view(), name='book_detail'),
    path('deletebook/<slug:slug>/', views.DeleteBook.as_view(), name='delete_book'),
    path('borrow_book/<int:book_id>', views.borrow_book, name='borrow_book'),
    path('return_book/<int:book_id>', views.return_book, name='return_book'),
    path('borrowed-books/', views.borrowed_books, name='borrowed_books'),
    path('categories/', views.categories, name='categories'),
    path('categories/<slug:category_slug>/', views.books_by_category, name='books_by_category'),
]