from django.contrib import admin
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'date_added')
    search_fields = ('title', 'text')
    list_filter = ('date_added', 'owner')
