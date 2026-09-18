"""
Class-based views managing editorial publications feed directories, search and category
filtering indexes, transactional comment moderations, and optimized content increments.
"""

from django.conf import settings
from django.db.models import Q, F
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, View

from .models import BlogPost, BlogCategory, BlogComment


class BlogListView(ListView):
    """
    Renders the central publications feed. Integrates query search mapping
    and category classifications side-by-side with paginated standard results.
    """
    model = BlogPost
    template_name = "blog/blog_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        """Builds filtering and global search context evaluations recursively."""
        queryset = BlogPost.objects.filter(is_published=True).select_related("category", "author")
        
        # 1. Map category selection checks
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            
        # 2. Map global keyword search parameters
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Load structural assets to drive taxonomy lists and layout metrics
        context["categories"] = BlogCategory.objects.all()
        context["featured_posts"] = BlogPost.objects.filter(is_published=True, is_featured=True)[:2]
        context["active_category"] = self.request.GET.get("category", "")
        context["search_query"] = self.request.GET.get("q", "")

        # SEO configurations — intent-led, human-readable
        context["seo_title"] = "Website, SEO & AI Insights for Growing Businesses"
        context["seo_description"] = (
            "Practical guides on website development costs, hiring a web developer, "
            "local SEO, WhatsApp lead generation and AI automation — by GrowthSpare IT Solutions."
        )
        # Internal search and filtered category pages must not be indexed as
        # separate pages (thin duplicates of the main blog index).
        if context["search_query"] or context["active_category"] or self.request.GET.get("page"):
            # Only search/filter combos are noindex; plain pagination page 1 stays indexable
            if context["search_query"] or context["active_category"]:
                context["seo_robots"] = "noindex, follow"
        base_url = settings.SITE_URL.rstrip("/")
        context["schema_data"] = [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base_url}/"},
                    {"@type": "ListItem", "position": 2, "name": "Insights", "item": f"{base_url}{reverse('blog:list')}"},
                ],
            }
        ]
        return context


class BlogPostDetailView(DetailView):
    """
    Dynamic article delivery platform. Optimizes relational queries, records
    traffic metrics safely, and pulls approved comments and context-related articles.
    """
    model = BlogPost
    template_name = "blog/blog_detail.html"
    context_object_name = "post"
    slug_url_kwarg = "slug"

    def get_object(self, queryset=None):
        """Safely increments the views metric upon direct layout hits."""
        post = super().get_object(queryset)
        
        # High-concurrency safe increment execution mapping using SQL expressions
        BlogPost.objects.filter(pk=post.pk).update(views_count=F("views_count") + 1)
        post.refresh_from_db(fields=["views_count"])
        return post

    def get_queryset(self):
        """Ensure only published blog nodes are retrieved."""
        return BlogPost.objects.filter(is_published=True).select_related("category", "author")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        # Retrieve up to 3 similar publications within same grouping, excluding current
        context["related_posts"] = (
            BlogPost.objects.filter(category=post.category, is_published=True)
            .exclude(id=post.id)
            .select_related("category", "author")[:3]
        )
        
        # Fetch approved comments
        context["approved_comments"] = post.comments.filter(is_approved=True)

        # SEO dynamic parameters
        context["seo_title"] = post.meta_title if post.meta_title else post.title
        context["seo_description"] = (
            post.meta_description
            if post.meta_description
            else post.content[:150] + "..."
        )

        # Article dynamic metadata structured block mapping
        context["schema_type"] = "Article"
        article_schema = {
            "@type": "Article",
            "headline": post.title,
            "author": {
                "@type": "Person",
                "name": f"{post.author.first_name} {post.author.last_name}".strip() or post.author.username,
            },
            "publisher": {
                "@type": "Organization",
                "@id": f"{settings.SITE_URL.rstrip('/')}/#organization",
                "name": "GrowthSpare IT Solutions",
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{settings.SITE_URL}/static/images/logo.png",
                },
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"{settings.SITE_URL}{post.get_absolute_url()}",
            },
            "keywords": post.tags,
        }
        if post.featured_image:
            try:
                img_url = post.featured_image.url
            except Exception:
                img_url = getattr(post.featured_image, "name", "")
            if img_url and not img_url.startswith("http"):
                base = settings.SITE_URL.rstrip("/")
                img_url = f"{base}{img_url}" if img_url.startswith("/") else f"{base}/{img_url}"
            if img_url:
                article_schema["image"] = img_url
        if post.published_at:
            article_schema["datePublished"] = post.published_at.isoformat()
        if post.updated_at:
            article_schema["dateModified"] = post.updated_at.isoformat()
        base_url = settings.SITE_URL.rstrip("/")
        breadcrumb_schema = {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base_url}/"},
                {"@type": "ListItem", "position": 2, "name": "Insights", "item": f"{base_url}{reverse('blog:list')}"},
                {"@type": "ListItem", "position": 3, "name": post.title, "item": f"{base_url}{post.get_absolute_url()}"},
            ],
        }
        context["schema_data"] = [article_schema, breadcrumb_schema]
        return context


class CommentCreateView(View):
    """Secure receiver logging post responses and queuing moderation tasks."""

    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(BlogPost, slug=slug, is_published=True)
        
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        content = request.POST.get("content", "").strip()

        if not name or not email or not content:
            messages.error(request, "All inputs are required to submit an editorial response.")
            return redirect(post.get_absolute_url())

        # Direct safe object generation
        BlogComment.objects.create(
            post=post,
            name=name,
            email=email,
            content=content,
            is_approved=False,  # Enforce strict moderation state before publishing
        )

        messages.success(
            request,
            "Thank you! Your response was logged and queued for administrative validation moderation.",
        )
        return redirect(post.get_absolute_url())