# Generated by Django 4.0 on 2021-12-31 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_alter_productimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='created_date',
            field=models.DateField(auto_now=True),
        ),
    ]
