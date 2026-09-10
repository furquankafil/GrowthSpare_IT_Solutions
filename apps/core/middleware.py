"""
Canonical-host redirect middleware (SEO safety).

301 redirects www.growthspareitsolutions.com -> growthspareitsolutions.com
preserving path + query. Only acts on that exact www host; all other hosts
(localhost, preview domains, apex) pass through untouched so local dev,
health checks and staging previews never break.
"""


class WwwToApexRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0].lower()
        if host == "www.growthspareitsolutions.com":
            path = request.get_full_path()
            return_https = "https://growthspareitsolutions.com" + path
            from django.http import HttpResponsePermanentRedirect

            return HttpResponsePermanentRedirect(return_https)
        return self.get_response(request)
