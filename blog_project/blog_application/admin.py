from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class BlogUserAdmin(UserAdmin):
    # Define the fields to be used in displaying the BlogUser model
    list_display = ('email', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email',)
    ordering = ('-date_joined',)

    # The fields to be used for user creation and change forms
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

admin.site.register(BlogUser, BlogUserAdmin)

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title',  'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content')
    filter_horizontal = ('tags',)
admin.site.register(BlogPost, BlogPostAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
admin.site.register(Tag, TagAdmin)

class LikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('post__title', 'user__email')

admin.site.register(Like, LikeAdmin)