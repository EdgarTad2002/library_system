from django.shortcuts import get_object_or_404, render
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from library.models import Book, Category, Borrow
from .serializers import BookSerializer, CategorySerializer, BorrowSerializer
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from .permissions import IsAdminOrReadOnly  

# Create your views here.
class BookViewSets(viewsets.ModelViewSet):
    # queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]

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


class BorrowedBooksAPIView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        borrowed_books_ids = Borrow.objects.filter(user=user, return_date__isnull=True).values_list('book', flat=True)
        return Book.objects.filter(id__in=borrowed_books_ids)
    

class BorrowBookAPIView(generics.CreateAPIView):
    serializer_class = BorrowSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Save the borrow record with the logged-in user"""
        serializer.save(user=self.request.user)

class ReturnBookAPIView(generics.UpdateAPIView):
    """API to return a borrowed book"""
    serializer_class = BorrowSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Find the active borrow record of the logged-in user for this book"""
        user = self.request.user
        book_id = self.kwargs.get("book_id")

        try:
            borrow = Borrow.objects.get(user=user, book_id=book_id, return_date__isnull=True)
        except Borrow.DoesNotExist:
            raise ValidationError("You have not borrowed this book or have already returned it.")

        return borrow