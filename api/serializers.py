from rest_framework import serializers
from library.models import Book, Category, Borrow
from django.utils import timezone
from datetime import timedelta

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book 
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BorrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ['book']
        

    def create(self, validated_data):
        """Ensure the book is not already borrowed"""
        user = self.context['request'].user
        book = validated_data['book']  # Get book instance from validated_data

        if Borrow.objects.filter(user=user, book=book, return_date__isnull=True).exists():
            raise serializers.ValidationError("You have already borrowed this book.")

        if book.copies_available == 0:
            raise serializers.ValidationError("No copies of this book are currently available.")

        book.copies_available -= 1
        book.save()

        # Create borrow record with a due date (3 days from now)
        borrow = Borrow.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=3),
            return_date=None  # Ensuring it's an active borrowing
        )

        return borrow

    def update(self, instance, validated_data):
        """Mark a book as returned"""
        if instance.return_date is not None:
            raise serializers.ValidationError("This book has already been returned.")

        instance.return_date = timezone.now()
        instance.book.copies_available += 1
        instance.book.save()
        instance.save()

        return instance

