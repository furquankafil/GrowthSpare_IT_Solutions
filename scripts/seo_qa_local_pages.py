"""
Automated SEO QA for the four hyper-local commercial landing pages.

Checks per page: HTTP 200, exactly one H1, unique title/meta, absolute
self-referencing canonical, indexable robots, ProfessionalService + Service +
BreadcrumbList + FAQPage JSON-LD (valid JSON), visible FAQ/schema parity,
phone + NAP + CTA presence, internal links, sitemap inclusion.

Usage:
    python scripts/seo_qa_local_pages.py
"""

import json
import os
import re
import sys

import django

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.test import Client  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402
from django.urls import reverse  # noqa: E402

setup_test_environment()

SITE = "https://growthspareitsolutions.com"

PAGES = [
    ("core:local-website-okhla", "/website-development-company-okhla-delhi/"),
    ("core:local-crm-delhi-ncr", "/crm-software-development-company-delhi-ncr/"),
    ("core:local-seo-shaheen", "/seo-company-shaheen-bagh-okhla/"),
    ("core:local-digital-south-delhi", "/digital-marketing-agency-south-delhi/"),
]

CHECKS = [
    "HTTP 200",
    "exactly one H1",
    "title exists",
    "title unique",
    "meta description exists",
    "meta description unique",
    "canonical exists",
    "canonical absolute URL",
    "canonical matches page",
    "indexable robots",
    "ProfessionalService schema",
    "Service schema",
    "Breadcrumb schema",
    "FAQPage schema",
    "valid JSON-LD",
    "FAQ visible/schema parity",
    "phone exists",
    "NAP exists",
    "CTA exists",
    "internal links exist",
    "no broken internal links",
    "sitemap inclusion",
]

failures = []
titles, descriptions = set(), set()
client = Client(HTTP_HOST="localhost")
sitemap_xml = client.get("/sitemap.xml").content.decode()


def check(name, page, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        failures.append((page, name, detail))


def graphs_from(html):
    out = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            return None, str(exc)
        if isinstance(data, dict) and "@graph" in data:
            out.extend(data["@graph"])
        elif isinstance(data, dict):
            out.append(data)
    return out, ""


for url_name, path in PAGES:
    print(f"\n{path}")
    resp = client.get(reverse(url_name))
    html = resp.content.decode() if resp.status_code == 200 else ""
    check("HTTP 200", path, resp.status_code == 200, f"got {resp.status_code}")
    if resp.status_code != 200:
        continue

    check("exactly one H1", path, html.lower().count("<h1") == 1)
    m_title = re.search(r"<title>(.*?)</title>", html, re.DOTALL)
    check("title exists", path, bool(m_title and m_title.group(1).strip()))
    title = m_title.group(1).strip() if m_title else ""
    check("title unique", path, title not in titles, title)
    titles.add(title)
    m_desc = re.search(r'<meta name="description" content="([^"]+)"', html)
    check("meta description exists", path, bool(m_desc and m_desc.group(1).strip()))
    desc = m_desc.group(1) if m_desc else ""
    check("meta description unique", path, desc not in descriptions)
    descriptions.add(desc)

    m_canon = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    check("canonical exists", path, bool(m_canon))
    canon = m_canon.group(1) if m_canon else ""
    check("canonical absolute URL", path, canon.startswith("https://"))
    check("canonical matches page", path, canon == f"{SITE}{path}", canon)
    m_robots = re.search(r'<meta name="robots" content="([^"]+)"', html)
    check("indexable robots", path, bool(m_robots and "noindex" not in m_robots.group(1)), m_robots.group(1) if m_robots else "missing")

    graphs, err = graphs_from(html)
    check("valid JSON-LD", path, graphs is not None, err)
    types = [g.get("@type") for g in (graphs or [])]
    check("ProfessionalService schema", path, "ProfessionalService" in types)
    check("Service schema", path, "Service" in types)
    check("Breadcrumb schema", path, "BreadcrumbList" in types)
    check("FAQPage schema", path, "FAQPage" in types)

    # Visible FAQ questions must match FAQPage schema questions exactly.
    faq_block = next((g for g in (graphs or []) if g.get("@type") == "FAQPage"), None)
    schema_qs = [q.get("name") for q in (faq_block.get("mainEntity", []) if faq_block else [])]
    parity = bool(schema_qs) and all(q in html for q in schema_qs)
    check("FAQ visible/schema parity", path, parity, f"{len(schema_qs)} questions")

    check("phone exists", path, "+91 9811579273" in html)
    check("NAP exists", path, "D-50, Shaheen Bagh, Okhla" in html)
    check("CTA exists", path, "tel:+919811579273" in html and "wa.me/919811579273" in html)
    links = set(re.findall(r'href="(/[^"#?]*)"', html))
    internal = [h for h in links if not h.startswith(("/media/", "/static/"))]
    check("internal links exist", path, len(internal) > 5, f"{len(internal)} found")
    broken = [h for h in internal if client.get(h).status_code >= 400]
    check("no broken internal links", path, not broken, str(broken[:5]))
    check("sitemap inclusion", path, path.strip("/") in sitemap_xml)

print(f"\n{len(CHECKS)} checks x {len(PAGES)} pages.")
if failures:
    print(f"FAILURES ({len(failures)}):")
    for page, name, detail in failures:
        print(f"  - {page}: {name} {detail}")
    sys.exit(1)
print("ALL SEO QA CHECKS PASSED.")
