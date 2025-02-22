from django.shortcuts import get_object_or_404, render, redirect
from .models import Book, Borrow, Category
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from .forms import AddBookForm
from .utils import SuperuserRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import timedelta, date, timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.

def home(request):
    query = request.GET.get('q')
    books = Book.objects.all()
    message = "Available Books"

    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )

    context = {
        'books': books,
        'query': query,
        'message': message,
    }

    return render(request, 'library/index.html', context)

 
class AddBook(SuperuserRequiredMixin, CreateView):
    form_class = AddBookForm
    template_name = 'library/book_form.html'
    success_url = '/'


class BookDetail(DetailView):
     
    template_name = 'library/book.html'
    slug_url_kwarg = 'book_slug'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        print(context['book'].title)
        context['title'] = context['book'].title

        if self.request.user.is_authenticated:
            is_borrowed = Borrow.objects.filter(
                user=self.request.user,
                book=context['book'],
                return_date__isnull=True
            ).exists()
        else:
            is_borrowed = False
        
        # Add the result to the context
        context['is_borrowed'] = is_borrowed

        return context
        
    
    def get_object(self, queryset=None):
        return get_object_or_404(Book, slug=self.kwargs[self.slug_url_kwarg])
    


class UpdatePage(SuperuserRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'content', 'isbn', 'publisher','category', 'copies_available', 'photo', 'slug']
    template_name = 'library/book_form.html'
    success_url = '/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Change Book Information'
        context['is_update'] = True
        return context
    

class DeleteBook(SuperuserRequiredMixin, DeleteView):
    model = Book 
    success_url = '/'
    template_name = 'library/delete_book.html'


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Check if copies are available
    if book.copies_available == 0:
        messages.error(request, "No copies of this book are currently available.")
        return redirect("book_detail", book_slug=book.slug)

    existing_borrow = Borrow.objects.filter(user=request.user, book=book, return_date__isnull=True).exists()
    if existing_borrow:
        messages.error(request, "You have already borrowed this book and have not returned it yet.")
        return redirect("book_detail", book_slug=book.slug)

    # Create a borrow instance
    borrow_instance = Borrow.objects.create(
        user=request.user,
        book=book,
        due_date=date.today() + timedelta(days=3)  # Example: 14-day loan period
    )

    # Decrease available copies
    book.copies_available -= 1
    book.save()

    send_mail(
                subject=f"Book Borrowed: {book.title}",
                message = f"""
Dear {request.user.username},

You have successfully borrowed the book "{book.title}". Please return it by {borrow_instance.due_date}.

Best regards,
DigitalLibrary Team
""",
                from_email=f"DigitalLibrary <{settings.DEFAULT_FROM_EMAIL}>",
                recipient_list=[request.user.email],
                fail_silently=True,
            )

    messages.success(request, f"You have successfully borrowed {book.title}!")
    return redirect("borrowed_books")


@login_required
def return_book(request, book_id):
    # Get the book or return a 404 error if it doesn't exist
    book = get_object_or_404(Book, id=book_id)

    # Check if the user has borrowed this book and hasn't returned it
    existing_borrow = Borrow.objects.filter(user=request.user, book=book, return_date__isnull=True).first()
    
    if not existing_borrow:
        messages.error(request, "You cannot return this book as you have not borrowed it before.")
        return redirect("borrowed_books")

    # Mark the book as returned by setting the return_date
    existing_borrow.return_date = date.today()
    existing_borrow.save()

    # Increase available copies
    book.copies_available += 1
    book.save()

    # Success message
    messages.success(request, f"You have successfully returned {book.title}!")
    return redirect("borrowed_books")


@login_required
def borrowed_books(request):
    # Fetch borrowed books for the current user
    borrowed_books = Borrow.objects.filter(user=request.user, return_date__isnull=True)  # Only show books that haven't been returned
    return render(request, 'library/borrowed_books.html', {'borrowed_books': borrowed_books})



def categories(request):
    # Fetch all categories from the database
    categories = Category.objects.all()
    
    # Pass the categories to the template
    return render(request, 'library/categories.html', {'categories': categories})


def books_by_category(request, category_slug):
    # Fetch the specific category or return a 404 error if not found
    category = get_object_or_404(Category, slug=category_slug)
    
    # Fetch books in this category
    books = Book.objects.filter(category=category)
    
    # Handle search query
    query = request.GET.get('q')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )
    
    # Custom message for the category page
    message = f"Books in the '{category.name}' category"
    
    # Pass the category, books, and message to the template
    context = {
        'books': books,
        'message': message,
        'category': category,
        'query': query,  # Pass the query to the template
    }
    return render(request, 'library/index.html', context)

    