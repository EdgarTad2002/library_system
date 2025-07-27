from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    logo = models.ImageField(upload_to="photos/%Y/%m/%d/", default=None,
                              blank=True, null=True, verbose_name="Logo")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, null=True)

    def  __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    content = models.TextField(blank=True, verbose_name="Book Description")
    isbn = models.CharField(max_length=13, unique=True)
    publisher = models.CharField(max_length=100)
    category = models.ManyToManyField(Category, related_name='books')
    copies_available = models.IntegerField()
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", default=None,
                              blank=True, null=True, verbose_name="Фото")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, null=True,
                            validators=[
                               MinLengthValidator(5, message="Минимум 5 символов"),
                               MaxLengthValidator(100, message="Максимум 100 символов"),
                            ])


    def __str__(self):
        return self.title
    

class Borrow(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"
    
    def save(self, *args, **kwargs):
        # Truncate seconds and microseconds from datetime fields
        if self.borrow_date is not None:
            self.borrow_date = self.borrow_date.replace(second=0, microsecond=0)
        if self.due_date is not None:
            self.due_date = self.due_date.replace(second=0, microsecond=0)
        if self.return_date is not None:
            self.return_date = self.return_date.replace(second=0, microsecond=0)
        super().save(*args, **kwargs)

    def is_overdue(self):
        """Check if the book is overdue."""
        return self.return_date is None and timezone.now() > self.due_date
    

class Reserve(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Fulfilled', 'Fulfilled'),
        ('Canceled', 'Canceled'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    reserve_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    notified = models.BooleanField(default=False)  
    expiry_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} reserved {self.book.title} at {self.reserve_date}"

    class Meta:
        ordering = ['reserve_date']
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'

    def save(self, *args, **kwargs):
        if not self.reserve_date:
            self.reserve_date = timezone.now()

        if not self.expiry_date:
            self.expiry_date = self.reserve_date + timedelta(days=3)
        super().save(*args, **kwargs)


class DailyTaskRun(models.Model):
    task_name = models.CharField(max_length=255, unique=True, help_text="Unique name for the scheduled task")
    last_run_datetime = models.DateTimeField(default=timezone.now,
                                            help_text="The exact datetime the task last ran")

    class Meta:
        verbose_name = "Daily Task Run"
        verbose_name_plural = "Daily Task Runs"

    def __str__(self):
        return f"{self.task_name} last ran on {self.last_run_datetime.date()} at {self.last_run_datetime.time()}"