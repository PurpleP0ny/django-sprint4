from django.urls import include, path

from . import views

app_name = 'blog'

post_endpoints = [
    path(
        '<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        '<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        '<post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        '<int:post_id>/comment/',
        views.AddCommentView.as_view(),
        name='add_comment'
    ),
    path(
        '<int:post_id>/edit_comment/<comment_id>/',
        views.EditCommentView.as_view(),
        name='edit_comment'
    ),
    path(
        '<int:post_id>/delete_comment/<comment_id>/',
        views.DeleteCommentView.as_view(),
        name='delete_comment'
    ),
    path(
        'create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
]

profile_endpoints = [
    path('<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('edit/', views.EditProfileView.as_view(), name='edit_profile'),
]

category_endpoints = [
    path(
        '<slug:category_slug>/',
        views.CategoryPostsView.as_view(),
        name='category_posts'
    ),
]

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/', include(post_endpoints)),
    path('profile/', include(profile_endpoints)),
    path('category/', include(category_endpoints)),
    path(
        'accounts/profile/',
        views.EditProfileView.as_view(),
        name='edit_profile'
    ),
]
