"""
Administrative dashboard configurations for showcase case studies management,
enabling rich multi-image gallery uploads and multi-category mappings.
"""

from django.contrib import admin
from .models import ProjectCategory, Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    """Enables multi-image uploads matching client interface gallery requirements."""
    model = ProjectImage
    extra = 3
    classes = ("collapse",)


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for project groups and classification labels."""
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Control room dashboard managing enterprise milestones, client information,
    problem/solution statements, performance metrics, and dynamic SEO settings.
    
    Updated to support safe multi-category filter selections horizontally.
    """
    inlines = [ProjectImageInline]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories",)  # Enables clean multi-category pick lists
    
    list_display = (
        "title",
        "client_name",
        "get_categories",  # Custom helper displaying mapped classifications cleanly
        "is_featured",
        "project_duration",
        "created_at",
    )
    list_filter = ("is_featured", "categories", "industry", "created_at")
    search_fields = (
        "title",
        "client_name",
        "industry",
        "problem_statement",
        "solution_statement",
        "results_statement",
        "technology_stack",
    )
    
    fieldsets = (
        (
            "Client & Scope",
            {
                "fields": (
                    "title",
                    "slug",
                    "client_name",
                    "industry",
                    "categories",
                    "is_featured",
                )
            },
        ),
        (
            "Visual Asset Settings",
            {
                "fields": (
                    "featured_image",
                    "video_url",
                )
            },
        ),
        (
            "Problem-Solving Metrics",
            {
                "description": "Details framing the strategic problem solved, specific solutions executed, and core outcomes.",
                "fields": (
                    "problem_statement",
                    "solution_statement",
                    "results_statement",
                ),
            },
        ),
        (
            "Specifications & Keywords",
            {
                "fields": (
                    "technology_stack",
                    "project_duration",
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

    def get_categories(self, obj):
        """Compiles associated categories into a comma-separated list for index views."""
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = "Assigned Categories"