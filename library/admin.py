from django.contrib import admin
from .models import Book, Borrow, Category, DailyTaskRun
# Register your models here.


admin.site.register(Book)
admin.site.register(Borrow)
admin.site.register(Category)
admin.site.register(DailyTaskRun)