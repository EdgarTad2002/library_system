from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import Borrow, DailyTaskRun
import logging

logger = logging.getLogger(__name__)

def send_reminder_emails():
    # Send reminders 2 days before the due date

    task_name = "send_reminder_emails"
    today = timezone.localdate()

    try:
        task_run, created = DailyTaskRun.objects.get_or_create(
            task_name=task_name,
            defaults={'last_run_datetime': timezone.now()}
        )

        # Check if it was NOT created and the date part of its last_run_datetime is TODAY
        if not created and task_run.last_run_datetime.date() == today:
            logger.info(f"'{task_name}' already ran today ({today}). Skipping.")
            return

        # If we are here, either it's a new task record, or it's a new day
        # Update the last run datetime for now
        task_run.last_run_datetime = timezone.now()
        task_run.save()
        logger.info(f"'{task_name}' status updated to run for {today}.")

    except Exception as e:
        logger.error(f"Error checking/updating DailyTaskRun for {task_name}: {e}", exc_info=True)
        # If there's a database error here, it's safer to stop and prevent sending emails twice
        # or not at all, depending on your error handling strategy.
        # For this case, we'll return to prevent potential issues.
        return
    
    logger.info(f"Running '{task_name}' task for {today} at {timezone.now()}...")

    target_date = timezone.now() + timedelta(days=2)
    borrows = Borrow.objects.filter(due_date__lte=target_date, return_date__isnull=True)

    if not borrows.exists():
        logger.info(f"No borrows found requiring a reminder for {target_date}.")
        logger.info(f"'{task_name}' task completed for {today}.")
        return
    
    sent_emails_count = 0

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

        logger.info(f"Sent reminder for '{borrow.book.title}' to {borrow.user.email} (Due: {borrow.due_date})")
        sent_emails_count += 1

    logger.info(f"'{task_name}' task completed for {today}. Sent {sent_emails_count} reminder emails.")


def auto_return_overdue_books():
    # Automatically return overdue books
    reminder_date = timezone.now() + timedelta(days=0)
    print(reminder_date)
    overdue_borrows = Borrow.objects.filter(due_date__lte=reminder_date, return_date__isnull=True)
    print(overdue_borrows)
   
   
    for borrow in overdue_borrows:
        borrow.return_date = timezone.now()
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