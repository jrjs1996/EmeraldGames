from django.contrib import admin
from main.models import Category, Thread, Message

# Register your models here.
admin.site.register(Category)
admin.site.register(Thread)
admin.site.register(Message)