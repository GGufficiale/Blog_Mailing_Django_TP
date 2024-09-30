from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from pytils.translit import slugify
from blog.models import Blog


class BlogListView(ListView):
    """Класс, заменяющий функцию product_list (FBV на CBV)"""
    model = Blog
    success_url = reverse_lazy('blog:blog_list')

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter()
        # Если нужно, чтоб вылезали только активированные товары, то используем это:
        # queryset = queryset.filter(is_published=True)
        return queryset


class BlogDetailView(DetailView):
    model = Blog

    def get_object(self, queryset=None):
        """Метод для подсчета к-ва просмотров страницы"""
        self.object = super().get_object()
        self.object.views_counter += 1
        self.object.save()
        return self.object


class BlogCreateView(CreateView):
    model = Blog
    fields = ("name", 'description', 'photo', 'views_counter')
    success_url = reverse_lazy('blog:blog_list')

    def form_valid(self, form):
        if form.is_valid():
            new_mat = form.save()
            new_mat.slug = slugify(new_mat.name)
            new_mat.save()
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
    """Функция-контроллер для изменения статуса активности записи блога"""
    blog_item = get_object_or_404(Blog, pk=pk)
    if blog_item.is_published:
        blog_item.is_published = False
    else:
        blog_item.is_published = True
    blog_item.save()
    return redirect(reverse('blog:blog_list'))
