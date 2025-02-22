from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import Borrow


def send_reminder_emails():
    # Send reminders 2 days before the due date
    reminder_date = timezone.now().date() + timedelta(days=2)
    borrows = Borrow.objects.filter(due_date__lte=reminder_date, return_date__isnull=True)

    for borrow in borrows:
        send_mail(
            subject=f"Reminder: Return {borrow.book.title}",
            message=f"""
            Dear {borrow.user.username},

            Please return {borrow.book.title} by {borrow.due_date}.
            
            Best regards,
            DigitalLibrary Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[borrow.user.email],
            fail_silently=True,
        )


def auto_return_overdue_books():
    # Automatically return overdue books
    overdue_borrows = Borrow.objects.filter(due_date__lte=timezone.now().date(), return_date__isnull=True)
    print(overdue_borrows)
    print(timezone.now().date())
    for borrow in overdue_borrows:
        borrow.return_date = timezone.now().date()
        borrow.save()

        # Increase available copies
        book = borrow.book
        book.copies_available += 1
        book.save()

        # Notify the user
        send_mail(
            subject=f"Book Automatically Returned: {borrow.book.title}",
            message=f"""
Dear {borrow.user.username},

The book {borrow.book.title} has been automatically returned as it was overdue.

Best regards,
DigitalLibrary Team""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[borrow.user.email],
            fail_silently=True,
        )