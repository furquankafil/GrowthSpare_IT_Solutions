"""
Administrative control panel configurations for managing editorial posts,
blog categorizations, and comment moderation metrics.
"""

from django.contrib import admin
from .models import BlogCategory, BlogPost, BlogComment


class BlogCommentInline(admin.TabularInline):
    """Enables comment review and configuration inline within the blog post admin view."""
    model = BlogComment
    extra = 0
    readonly_fields = ("name", "email", "content", "created_at")
    can_delete = True
    classes = ("collapse",)


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for post classifications and tag categories."""
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """
    Control room interface managing active blog entries, author profiles,
    and search index optimization parameters.
    """
    inlines = [BlogCommentInline]
    prepopulated_fields = {"slug": ("title",)}
    
    list_display = (
        "title",
        "author",
        "category",
        "is_published",
        "is_featured",
        "views_count",
        "published_at",
    )
    list_filter = ("is_published", "is_featured", "category", "author", "published_at")
    search_fields = ("title", "content", "tags")
    actions = ["publish_articles", "unpublish_articles"]
    
    fieldsets = (
        (
            "Publication Core Details",
            {
                "fields": (
                    "title",
                    "slug",
                    "author",
                    "category",
                )
            },
        ),
        (
            "State & Promotion Settings",
            {
                "fields": (
                    "is_published",
                    "is_featured",
                    "featured_image",
                )
            },
        ),
        (
            "Editorial Copy Content",
            {
                "fields": (
                    "content",
                    "tags",
                )
            },
        ),
        (
            "Hardened Search Optimization (SEO)",
            {
                "classes": ("collapse",),
                "fields": (
                    "meta_title",
                    "meta_description",
                ),
            },
        ),
    )

    def publish_articles(self, request, queryset):
        """Action method enabling mass-publishing of draft entries."""
        updated = queryset.update(is_published=True)
        # Call save trigger sequentially to update publishing timestamps safely
        for obj in queryset:
            obj.save()
        self.message_user(request, f"Successfully activated {updated} editorial publications.")
    publish_articles.short_description = "Publish selected blog entries"

    def unpublish_articles(self, request, queryset):
        """Action method enabling mass-unpublishing of active entries."""
        updated = queryset.update(is_published=False)
        for obj in queryset:
            obj.save()
        self.message_user(request, f"Successfully deactivated {updated} editorial publications.")
    unpublish_articles.short_description = "Unpublish selected blog entries"


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    """Moderation control panel ensuring complete control over potential comments spam."""
    list_display = ("name", "email", "post", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("name", "email", "content")
    actions = ["approve_comments", "reject_comments"]

    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"Successfully validated and approved {updated} client comments.")
    approve_comments.short_description = "Approve selected reader comments"

    def reject_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"Successfully rejected {updated} reader comments.")
    reject_comments.short_description = "Reject selected reader comments"