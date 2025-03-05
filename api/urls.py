from django.urls import include, path 
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'books', views.BookViewSets, basename='api-books')

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', views.CategoryListAPIView.as_view(), name='api-categories'),
    path('categories/<str:category_slug>/books/', views.BooksByCategoryAPIView.as_view(), name='api-category-books'),
]

