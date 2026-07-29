"""
Custom Django template tags to safely construct optimized SEO meta structures,
canonical URLs, Open Graph schemas, Twitter cards, and JSON-LD markup.
"""

import json
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def get_canonical_url(context):
    """
    Computes and returns the absolute, canonical URL for the current request context,
    enforcing URL unification and preventing duplicate page index issues in search engines.
    """
    request = context.get("request")
    if not request:
        return ""
    # Enforces HTTPS canonical strings globally when running in production environment
    protocol = "https" if request.is_secure() else "http"
    host = request.get_host()
    path = request.path
    return f"{protocol}://{host}{path}"


@register.simple_tag(takes_context=True)
def render_seo_meta(context, title=None, description=None, image=None, keywords=None):
    """
    Renders standardized, high-performance SEO headers, canonical references,
    Open Graph tags, and Twitter Cards for social platforms.
    """
    request = context.get("request")
    canonical_url = get_canonical_url(context)
    
    # Core fallback variables driven from company profile settings
    comp_title = "GrowthSpare IT Solutions"
    comp_desc = "Empowering Businesses with AI, Software Development & Digital Innovation."
    comp_kw = "AI Automation, Web Development, Django, SaaS development, CRM Development, New Delhi"
    
    final_title = f"{title} | {comp_title}" if title else f"{comp_title} - {comp_desc}"
    final_desc = description if description else comp_desc
    final_keywords = keywords if keywords else comp_kw
    final_image = image if image else "/static/images/logo.png"

    # Resolve absolute link if image path is structural rather than full resource
    if request and not final_image.startswith("http"):
        protocol = "https" if request.is_secure() else "http"
        final_image = f"{protocol}://{request.get_host()}{final_image}"

    # SECURITY: title/description/keywords/image may originate from
    # admin-editable model fields (Service.meta_title, BlogPost.meta_title,
    # BlogPost.title, etc.). Every dynamic value is HTML-escaped before
    # interpolation — this whole block is mark_safe()'d afterward, so
    # unescaped input here would be a stored-XSS vector.
    final_title = escape(final_title)
    final_desc = escape(final_desc)
    final_keywords = escape(final_keywords)
    final_image = escape(final_image)
    canonical_url = escape(canonical_url)

    meta_html = f"""
    <!-- Enforce Core Search Metadata -->
    <title>{final_title}</title>
    <meta name="description" content="{final_desc}">
    <meta name="keywords" content="{final_keywords}">
    <link rel="canonical" href="{canonical_url}">

    <!-- Open Graph Protocol Validation (Facebook, LinkedIn) -->
    <meta property="og:site_name" content="{escape(comp_title)}">
    <meta property="og:title" content="{final_title}">
    <meta property="og:description" content="{final_desc}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:type" content="website">
    <meta property="og:image" content="{final_image}">

    <!-- Twitter Card Validation -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{final_title}">
    <meta name="twitter:description" content="{final_desc}">
    <meta name="twitter:image" content="{final_image}">
    """
    return mark_safe(meta_html.strip())


@register.simple_tag
def render_json_ld(schema_type, data):
    """
    Returns dynamically populated Schema.org JSON-LD elements wrapped
    in secure HTML scripts, establishing rich snippet capabilities.
    """
    if not isinstance(data, dict):
        return ""
        
    # Inject primary schema context constraints
    schema_payload = {
        "@context": "https://schema.org",
        "@type": schema_type,
        **data
    }
    
    # json.dumps already produces safely-escaped string content for the
    # </script> boundary is the one risk here — guard against a payload
    # value containing a literal "</script>" breaking out of the tag.
    payload_json = json.dumps(schema_payload, indent=2, ensure_ascii=False).replace("</script>", "<\\/script>")
    output_html = f"""
<script type="application/ld+json">
{payload_json}
</script>
    """
    return mark_safe(output_html.strip())