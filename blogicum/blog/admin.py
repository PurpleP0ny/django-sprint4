from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User
from django.utils.html import format_html

from .models import Category, Comment, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at'
    )
    list_editable = ('is_published',)
    list_filter = ('is_published', 'category', 'author', 'location')
    search_fields = ('title', 'text')
    date_hierarchy = 'pub_date'
    raw_id_fields = ('author', 'location', 'category')

    @admin.display(description='Комментарии')
    def comment_count(self, obj):
        return obj.comments.count()

    @admin.display(description='Изображение')
    def display_name(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" />',
                obj.image.url
            )
        return 'Изображение отсутсвует'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'post', 'created_at')
    list_filter = ('author', 'post', 'created_at')
    search_fields = ('text',)
    raw_id_fields = ('author', 'post')


class SimpleUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('post_count',)

    @admin.display(description='Количество постов')
    def post_count(self, obj):
        return obj.posts.count()


admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, SimpleUserAdmin)
