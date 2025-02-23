from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth import get_user_model

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
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"