from django.contrib import admin
from blog.models import Blog

"""Вывод списка записей блога"""


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('name', 'description',)

