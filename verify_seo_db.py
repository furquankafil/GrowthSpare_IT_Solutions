import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
import django
django.setup()
from apps.blog.models import BlogPost
from apps.services.models import Service
from apps.core.context_processors import COMPANY_NAME

print("=== BLOG POSTS ===")
posts = BlogPost.objects.filter(is_published=True).select_related("category", "author")
print(f"Total published: {posts.count()}")
for p in posts.order_by("-published_at"):
    meta_title = p.meta_title[:60] if p.meta_title else "(none)"
    meta_desc = p.meta_description[:60] if p.meta_description else "(none)"
    print(f"  {p.title[:60]}")
    print(f"    slug={p.slug} | meta_title={meta_title} | meta_desc={meta_desc} | content_len={len(p.content)}")

print()
print("=== SERVICES ===")
svcs = Service.objects.filter(is_active=True)
print(f"Total active services: {svcs.count()}")
for s in svcs:
    meta_title = s.meta_title[:60] if s.meta_title else "(none)"
    cta = s.cta_headline[:50] if s.cta_headline else "(none)"
    print(f"  {s.title} | slug={s.slug} | meta={meta_title} | cta={cta}")

print()
print("=== CONFIG ===")
from django.conf import settings
print(f"SITE_URL: {settings.SITE_URL}")
print(f"DEBUG (dev): {settings.DEBUG}")
print(f"ALLOWED_HOSTS (dev): {settings.ALLOWED_HOSTS}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
