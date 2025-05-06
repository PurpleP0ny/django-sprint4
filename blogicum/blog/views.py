from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .constants import VIEWS_PAGINATE_BY
from .forms import CommentForm, PostForm, UserProfileForm
from .models import Category, Comment, Post

User = get_user_model()


class AuthorTestMixin(UserPassesTestMixin):

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class CommentTestMixin(UserPassesTestMixin):

    def test_func(self):
        comment = super().get_object()
        return comment.author == self.request.user


class PostListView(ListView):
    model = Post
    paginate_by = VIEWS_PAGINATE_BY
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.objects.published(
        ).with_related().with_comments_count(
        ).order_by('-pub_date')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostUpdateView(LoginRequiredMixin, AuthorTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    login_url = None
    raise_exception = False

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class PostDeleteView(LoginRequiredMixin, AuthorTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        return Post.objects.select_related('author', 'category', 'location')

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            post = super().get_object(queryset)
            if post.author == self.request.user:
                return post
        except Http404:
            pass
        return super().get_object(
            queryset.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        )

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            form=CommentForm(),
            comments=self.object.comments.select_related(
                'author').order_by('created_at')
        )


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = VIEWS_PAGINATE_BY

    def get_profile_user(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        profile_user = self.get_profile_user()
        queryset = profile_user.posts.annotate(
            comment_count=Count('comments')
        ).select_related(
            'category', 'location'
        ).order_by('-pub_date')
        if self.request.user != profile_user:
            queryset = queryset.filter(
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile_user()
        return context


class CategoryPostsView(ListView):
    model = Post
    paginate_by = VIEWS_PAGINATE_BY
    template_name = 'blog/category.html'

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        return (
            self.get_category().posts
            .filter(
                is_published=True,
                pub_date__lte=timezone.now()
            )
            .select_related('author', 'location')
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )

    def get_context_data(self, **kwargs):
        """Добавляет категорию в контекст"""
        return dict(
            **super().get_context_data(**kwargs),
            category=self.get_category()
        )


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


class EditCommentView(LoginRequiredMixin, CommentTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class DeleteCommentView(LoginRequiredMixin, CommentTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class UserCreateView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('blog:index')
