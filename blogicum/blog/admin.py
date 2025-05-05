from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, User

from .models import Category, Location, Post


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
    raw_id_fields = ('author',)


class SimpleUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('post_count',)

    @admin.display(description='Количество постов')
    def post_count(self, obj):
        return obj.posts.count()


admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, SimpleUserAdmin)
