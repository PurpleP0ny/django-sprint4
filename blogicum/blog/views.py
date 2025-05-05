from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, UserProfileForm
from .models import Category, Comment, Post

User = get_user_model()


class PostListView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_queryset(self):
        queryset = Post.published.order_by('-pub_date')
        return queryset.annotate(comment_count=Count('comments'))


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail', post_id=post.id)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        return post

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author != self.request.user:
            raise PermissionDenied("Вы не можете удалить этот пост")
        return post


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = get_object_or_404(
            Post.objects.select_related('author', 'category', 'location'),
            id=self.kwargs['post_id']
        )
        if (post.author == self.request.user
            or (post.is_published and post.category.is_published
                and post.pub_date <= timezone.now())):
            return post
        raise Http404("Страница не найдена")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all().order_by('created_at')
        return context


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        username = self.kwargs['username']
        profile = get_object_or_404(User, username=username)
        if self.request.user == profile:
            queryset = Post.objects.filter(author=profile)
        else:
            queryset = Post.published.filter(author=profile)
        return queryset.select_related(
            'author', 'category', 'location'
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs['username'])
        return context


class CategoryPostsView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True)
        queryset = Post.published.filter(category=self.category)
        return queryset.select_related(
            'author', 'category', 'location'
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.object.username}
        )

    def get_object(self):
        return self.request.user


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class EditCommentView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.author != self.request.user:
            raise PermissionDenied(
                "Вы не можете редактировать этот комментарий"
            )
        return comment

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.author != self.request.user:
            raise PermissionDenied("Вы не можете удалить этот комментарий")
        return comment

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class UserCreateView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('blog:index')
