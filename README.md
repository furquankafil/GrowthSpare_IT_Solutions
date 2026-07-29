# GrowthSpare IT Solutions Enterprise Platform

Enterprise-level, performance-optimized, and production-ready full-stack software platform for **GrowthSpare IT Solutions** (https://growthspareitsolutions.com). Built using Python 3.13, Django 6, PostgreSQL, Docker, Bootstrap 5, Tailwind CSS, GSAP, and AOS Animations.

---

## 🚀 System Architecture Overview

This project uses a domain-driven, multi-app Django architecture. Each business capability resides within its own modular application. This layout isolates responsibilities and allows you to scale, modify, or convert individual modules into standalone SaaS or CRM pipelines with minimal structural friction.

- **`config/`**: Operational control room housing environment routing, standard ASGI/WSGI engines, and settings profiles.
- **`apps/accounts/`**: Foundation for identity access, JWT operations, user profile state tracking, and permission schemes.
- **`apps/core/`**: Controls foundational interface views (Home, About, terms), sitemaps, robots configuration, and dynamic JSON-LD structured layout tags.
- **`apps/services/`**: Holds service models, custom landing page data models, processes, and tech tags.
- **`apps/portfolio/`**: Handles technical case studies (problem-solution metrics, client logos, dynamic filter states, video layouts).
- **`apps/blog/`**: Dynamic rich-text publication portal, categorizations, reading calculations, and search schemas.
- **`apps/contact/`**: Encrypted endpoint ingestion storing general incoming client leads.
- **`apps/consultation/`**: Secure multi-step consultation funnel for incoming project briefs.
- **`apps/faq/`**: Dynamic knowledge bases for self-service help and structured schema validation.
- **`apps/testimonials/`**: Reviews database powering social proof sliders.
- **`apps/dashboard/`**: Secure portal framework which serves as the direct seed for CRM or customer-facing operations.

---

## 🛠️ Tech Stack & Key Features

- **Backend**: Python 3.13+, Django 6, Django REST Framework, JWT.
- **Database**: PostgreSQL (Production), SQLite (local quick development).
- **Frontend**: Tailwind CSS, Bootstrap 5, GSAP, AOS, SwiperJS, Particles.js.
- **Deployment & Scaling**: Docker, Docker Compose, Nginx, Gunicorn, WhiteNoise, Redis.
- **Security & Hardening**: CSP Protection headers, Rate Limiting, secure CSRF/Cookie tokens, parameterized database queries.
- **SEO Optimization**: Dynamic JSON-LD structures, breadcrumb trackers, canonical link headers, structured sitemaps.

---

## 💻 Local Development Setup

Follow these steps to run the application locally on your host environment:

### 1. System Requirements
- Python 3.13+ installed
- PostgreSQL instance running (or utilize SQLite as default fallback)
- Virtual Environment tool (`venv` or `virtualenv`)

### 2. Environment Setup & Configuration
Clone this repository to your work directory:
```bash
git clone https://github.com/growthspare/growthspare-platform.git
cd growthspare-platform