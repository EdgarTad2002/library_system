# Generated by Django 4.2.11 on 2025-02-24 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0003_category_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrow',
            name='borrow_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='borrow',
            name='due_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='borrow',
            name='return_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
