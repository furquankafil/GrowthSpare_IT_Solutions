/**
 * GrowthSpare IT Solutions - Privacy-friendly conversion event tracking.
 * Sends GA4 events only if gtag is present; never blocks navigation.
 * Events: whatsapp_click, phone_click, email_click, audit_request_submit,
 * contact_submit, portfolio_click, consultation_start.
 */
(function () {
  "use strict";

  function track(eventName, params) {
    try {
      if (typeof window.gtag === "function") {
        window.gtag("event", eventName, params || {});
      }
    } catch (e) {
      /* no-op: tracking must never break UX */
    }
  }

  function bindWhatsApp() {
    document.querySelectorAll('a[href*="wa.me/"]').forEach(function (a) {
      if (a.dataset.ctBound) return;
      a.dataset.ctBound = "1";
      a.addEventListener("click", function () {
        var label = (a.getAttribute("aria-label") || a.textContent || "whatsapp").trim().slice(0, 100);
        track("whatsapp_click", { link_label: label, page_path: window.location.pathname });
      });
    });
  }

  function bindTelMail() {
    document.querySelectorAll('a[href^="tel:"]').forEach(function (a) {
      if (a.dataset.ctBound) return;
      a.dataset.ctBound = "1";
      a.addEventListener("click", function () {
        track("phone_click", { page_path: window.location.pathname });
      });
    });
    document.querySelectorAll('a[href^="mailto:"]').forEach(function (a) {
      if (a.dataset.ctBound) return;
      a.dataset.ctBound = "1";
      a.addEventListener("click", function () {
        track("email_click", { page_path: window.location.pathname });
      });
    });
  }

  function bindForms() {
    var consult = document.getElementById("scoping-multi-step-form");
    if (consult && !consult.dataset.ctBound) {
      consult.dataset.ctBound = "1";
      consult.addEventListener("submit", function () {
        track("audit_request_submit", { page_path: window.location.pathname });
      });
    }
    document.querySelectorAll('form[action*="/contact"]').forEach(function (f) {
      if (f.dataset.ctBound) return;
      f.dataset.ctBound = "1";
      f.addEventListener("submit", function () {
        track("contact_submit", { page_path: window.location.pathname });
      });
    });
    var newsletter = document.getElementById("footer-newsletter-form");
    if (newsletter && !newsletter.dataset.ctBound) {
      newsletter.dataset.ctBound = "1";
      newsletter.addEventListener("submit", function () {
        track("newsletter_submit", { page_path: window.location.pathname });
      });
    }
  }

  function bindPortfolio() {
    document.querySelectorAll('a[href*="/portfolio/"]').forEach(function (a) {
      if (a.dataset.ctBoundPf) return;
      a.dataset.ctBoundPf = "1";
      a.addEventListener("click", function () {
        track("portfolio_click", {
          link_label: (a.textContent || "").trim().slice(0, 100),
          page_path: window.location.pathname,
        });
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindWhatsApp();
    bindTelMail();
    bindForms();
    bindPortfolio();
  });
})();
