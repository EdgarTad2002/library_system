from django.shortcuts import get_object_or_404, render
from rest_framework import generics, viewsets
from library.models import Book, Category
from .serializers import BookSerializer, CategorySerializer
from django.db.models import Q

# Create your views here.
class BookViewSets(viewsets.ReadOnlyModelViewSet):
    # queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = Book.objects.all()
        query = self.request.query_params.get('q', None)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(isbn__icontains=query)
            )  # Case-insensitive search
        return queryset
    


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BooksByCategoryAPIView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        queryset = Book.objects.filter(category__slug=category_slug)

        query = self.request.query_params.get('q', None)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(isbn__icontains=query)
            )  # Case-insensitive search
        return queryset
