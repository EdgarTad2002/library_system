from django.shortcuts import get_object_or_404, render, redirect
from .models import Book, Borrow, Category, Reserve
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from .forms import AddBookForm
from .utils import SuperuserRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import timedelta
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mass_mail
from django.urls import reverse_lazy


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
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Register New Book"
        context['button_text'] = "Add Book"
        return context


class BookDetail(DetailView):
    model = Book
    template_name = 'library/book.html'
    slug_url_kwarg = 'book_slug'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        # Get the default context
        context = super().get_context_data(**kwargs)
        
        # Check if the user is authenticated and if the book is borrowed
        if self.request.user.is_authenticated:
            # Get the Borrow object if it exists
            borrowed_book = Borrow.objects.filter(
                user=self.request.user,
                book=context['book'],
                return_date__isnull=True
            ).first()
            
            # Check if the book is borrowed
            is_borrowed = borrowed_book is not None
            
            # Add due_date to context if the book is borrowed
            if is_borrowed:
                context['due_date'] = borrowed_book.due_date
        else:
            is_borrowed = False

        # Add the result to the context
        context['is_borrowed'] = is_borrowed
        is_available = context['book'].copies_available > 0
        context['is_available'] = is_available

        if self.request.user.is_authenticated:
            is_reserved = Reserve.objects.filter(user=self.request.user, book=context['book'], status="Pending").exists()
            context['is_reserved'] = is_reserved

        return context

    # def get_object(self, queryset=None):
    #     # Fetch the book object or return a 404 error if not found
    #     return get_object_or_404(Book, slug=self.kwargs[self.slug_url_kwarg])
    


class UpdatePage(SuperuserRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'content', 'publisher','category', 'copies_available', 'photo', 'slug']
    template_name = 'library/book_form.html'
    success_url = reverse_lazy('home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Book Details'
        context['button_text'] = "Save"
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
        due_date=timezone.now() + timedelta(days=10)  # Example: 10-day loan period
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
def reserve_book(request, book_id):

    book = get_object_or_404(Book, id=book_id)
    
    existing_borrow = Borrow.objects.filter(user=request.user, book=book, return_date__isnull=True).exists()
    if existing_borrow:
        messages.error(request, "You have already borrowed this book and have not returned it yet.")
        return redirect("book_detail", book_slug=book.slug)
    
    if book.copies_available > 0:
        messages.error(request, "Copies of this book are currently available. You can borrow it")
        return redirect("book_detail", book_slug=book.slug)
    
    existing_reserve = Reserve.objects.filter(user=request.user, book=book, status="Pending").exists()
    if existing_reserve:
        messages.error(request, "You have already reserved this book")
        return redirect("book_detail", book_slug=book.slug)
    
    reserve_instance = Reserve.objects.create(
        user=request.user,
        book = book,
        status="Pending"
    )

    messages.success(request, "You have successfully reserved this book. You will be notified when it becomes available.")

    # Redirect to the book detail page
    return redirect("book_detail", book_slug=book.slug)



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
    existing_borrow.return_date = timezone.now()
    existing_borrow.save()

    # Increase available copies
    book.copies_available += 1
    book.save()

    existing_reserves = Reserve.objects.filter(book=book, status="Pending")

    if existing_reserves.exists():
        # Prepare email data for all users
        email_subject = f"Book Available to Borrow: {book.title}"
        email_message = f"""
The book "{book.title}" is now available for borrowing. Please visit the library to borrow it.

Best regards,
DigitalLibrary Team
"""
        email_from = f"DigitalLibrary <{settings.DEFAULT_FROM_EMAIL}>"

        # Create a list of email tuples for send_mass_mail
        email_data = [
            (email_subject, email_message, email_from, [reserve.user.email])
            for reserve in existing_reserves
        ]

        # Send emails in bulk
        try:
            send_mass_mail(email_data, fail_silently=False)
        except Exception as e:
            # Log the error or handle it as needed
            print(f"Failed to send emails: {e}")

        # Update reservation statuses in bulk
        for reserve in existing_reserves:
            reserve.status = "Fulfilled"
        Reserve.objects.bulk_update(existing_reserves, ['status'])

    messages.success(request, f"You have successfully returned {book.title}!")
    return redirect("borrowed_books")


@login_required
def borrowed_books(request):
    # Fetch borrowed books for the current user
    borrowed_books = Borrow.objects.filter(user=request.user, return_date__isnull=True)  # Only show books that haven't been returned
    return render(request, 'library/borrowed_books.html', {'borrowed_books': borrowed_books})



def categories(request):
    # Fetch all categories from the database
    categories = Category.objects.filter(is_featured=True)

    
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

    