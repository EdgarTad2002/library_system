from django.urls import include, path, re_path 
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'books', views.BookViewSets, basename='api-books')

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', views.CategoryListAPIView.as_view(), name='api-categories'),
    path('categories/<str:category_slug>/books/', views.BooksByCategoryAPIView.as_view(), name='api-category-books'),
    path('borrowed-books/', views.BorrowedBooksAPIView.as_view(), name='api-borrowed-books'),
    path('borrow/', views.BorrowBookAPIView.as_view(), name='api-borrow-book'),
    path("return/", views.ReturnBookAPIView.as_view(), name="api-return-book"),
    path('auth/', include('djoser.urls')),          
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]

