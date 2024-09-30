from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from pytils.translit import slugify
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView

from blog.models import Blog
from blog.utils import get_cache_mailing_active, get_mailing_count_from_cache, get_cache_unique_quantity


class BlogListView(ListView):
    model = Blog
    template_name = 'blog/blog_list.html'
    extra_context = {'title': 'Блог'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_quantity_active'] = get_cache_mailing_active()
        context['mailing_quantity'] = get_mailing_count_from_cache()
        context['clients_unique_quantity'] = get_cache_unique_quantity()
        context['records'] = Blog.objects.order_by('?')[:3]
        return context


class BlogDetailView(DetailView):
    """Класс, заменяющий функцию products_detail (FBV на CBV)"""
    model = Blog

    def get_object(self, queryset=None):
        """Метод для подсчета к-ва просмотров страницы"""
        self.object = super().get_object()
        self.object.views_counter += 1
        self.object.save()
        return self.object


class BlogCreateView(CreateView):
    model = Blog
    fields = ['title', 'content', 'picture', 'is_active', 'number_of_views']
    template_name = 'blog/blog_form.html'
    success_url = reverse_lazy('blog:blog_list')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить запись в блог'
        return context

    def form_valid(self, form):
        if form.is_valid():
            new_blog = form.save()
            new_blog.slug = slugify(new_blog.title)
            new_blog.save()
        return super().form_valid(form)


class BlogUpdateView(UpdateView):
    model = Blog
    fields = ("name", 'description', 'photo', 'views_counter')
    success_url = reverse_lazy('blog:blog_list')

    def form_valid(self, form):
        if form.is_valid():
            new_mat = form.save()
            new_mat.slug = slugify(new_mat.name)
            new_mat.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:blog_detail', args=[self.kwargs.get('pk')])


class BlogDeleteView(DeleteView):
    model = Blog
    success_url = reverse_lazy('blog:blog_list')

    def get_object(self, queryset=None):
        """Метод для определения доступа к удалению только своих записей"""
        self.object = super().get_object(queryset)
        if self.request.user == self.object.owner or self.request.user.groups.filter(name='moderator').exists():
            return self.object
        raise PermissionDenied


def toggle_activity(request, pk):
    """Функция-контроллер для изменения статуса активности товара"""
    blog_item = get_object_or_404(Blog, pk=pk)
    if blog_item.is_published:
        blog_item.is_published = False
    else:
        blog_item.is_published = True
    blog_item.save()
    return redirect(reverse('blog:blog_list'))
