from django.db import models
from users.models import User

"""Создание модели для блога"""
NULLABLE = {'blank': True, 'null': True}  # форма, если параметр необязателен


class Blog(models.Model):
    name = models.CharField(max_length=100, verbose_name='заголовок')
    description = models.CharField(max_length=1000, verbose_name='содержимое')
    photo = models.ImageField(upload_to='blog/photo', verbose_name="фото в записи блога", **NULLABLE)
    # Для работы с изображениями в Джанго надо не забыть установить пакет Pillow"""
    created_at = models.DateField(**NULLABLE, verbose_name='дата создания записи', auto_now_add=True)
    views_counter = models.PositiveIntegerField(verbose_name='счетчик просмотров', help_text='укажите к-во просмотров',
                                                default=0)
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    slug = models.CharField(max_length=150, verbose_name='slug', null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='юзер', **NULLABLE,
                              related_name="user")

    # Сразу после внесения изменений в модель создаем миграцию"""

    def __str__(self):
        return f'{self.name}: {self.description}. К-во просмотров: {self.views_counter}'

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'записи'
        ordering = ['name', 'description', 'views_counter', ]
        permissions = [
            ('cancel_publication', 'Can cancel publication'),
            ('edit_description', 'Can edit description'),
            ('change_category', 'Can change category'),
        ]
