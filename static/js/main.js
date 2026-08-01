/**
 * GrowthSpare IT Solutions - Core Interface Operations Module
 * Handles scroll effects, active navigation trackers, lazy loading, and general back-to-top actions.
 */

document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    // Initialize core structural UI elements
    initBackToTop();
    initLazyLoading();
    initScrollHeader();
    initActiveNavTracker();
});

/**
 * Instantiates the performance-optimized Back to Top button.
 * Detects scroll thresholds and executes smooth vertical scroll transitions.
 */
function initBackToTop() {
    // Generate a beautiful, rounded back-to-top button dynamically
    const backToTopBtn = document.createElement("button");
    backToTopBtn.setAttribute("aria-label", "Scroll back to the top of the page");
    backToTopBtn.className = "fixed bottom-24 right-6 z-40 w-12 h-12 rounded-xl bg-slate-900/90 text-white dark:bg-white/95 dark:text-slate-900 flex items-center justify-center shadow-2xl border border-white/5 opacity-0 translate-y-3 pointer-events-none hover:scale-105 transition-all duration-300";
    backToTopBtn.innerHTML = '<i class="fas fa-arrow-up text-sm"></i>';
    document.body.appendChild(backToTopBtn);

    // Watch scroll position to trigger visibility
    window.addEventListener("scroll", () => {
        if (window.scrollY > 400) {
            backToTopBtn.classList.remove("opacity-0", "translate-y-3", "pointer-events-none");
            backToTopBtn.classList.add("opacity-100", "translate-y-0");
        } else {
            backToTopBtn.classList.add("opacity-0", "translate-y-3", "pointer-events-none");
            backToTopBtn.classList.remove("opacity-100", "translate-y-0");
        }
    });

    // Smooth scroll transition triggers
    backToTopBtn.addEventListener("click", () => {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    });
}

/**
 * Optimizes media performance metrics using native IntersectionObserver lazy loading,
 * preventing standard page-loading visual latency.
 */
function initLazyLoading() {
    const lazyImages = [].slice.call(document.querySelectorAll("img.lazy-load"));

    if ("IntersectionObserver" in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const image = entry.target;
                    image.src = image.dataset.src;
                    image.classList.remove("lazy-load");
                    imageObserver.unobserve(image);
                }
            });
        });

        lazyImages.forEach(image => {
            imageObserver.observe(image);
        });
    } else {
        // Fallback for older legacy browsers
        lazyImages.forEach(image => {
            image.src = image.dataset.src;
        });
    }
}

/**
 * Manages sticky navigation transforms. Applies standard shadow parameters
 * and adjusts spatial heights when page scrolling exceeds predefined boundaries.
 */
function initScrollHeader() {
    const header = document.getElementById("masthead");
    if (!header) return;

    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            header.classList.add("shadow-lg", "py-2");
            header.classList.remove("py-4");
        } else {
            header.classList.remove("shadow-lg", "py-2");
            header.classList.add("py-4");
        }
    });
}

/**
 * Highlights active section items inside the sticky navigation system.
 * Employs IntersectionObserver to track scroll depths and update menu classes.
 */
function initActiveNavTracker() {
    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll("nav a[href*='#']");
    if (sections.length === 0 || navLinks.length === 0) return;

    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const activeId = entry.target.getAttribute("id");
                
                navLinks.forEach(link => {
                    const href = link.getAttribute("href");
                    if (href.includes(activeId)) {
                        link.classList.add("text-primary", "dark:text-accent");
                        link.classList.remove("text-slate-600", "dark:text-slate-300");
                    } else {
                        link.classList.remove("text-primary", "dark:text-accent");
                        link.classList.add("text-slate-600", "dark:text-slate-300");
                    }
                });
            }
        });
    }, {
        threshold: 0.3,
        rootMargin: "-20% 0px -60% 0px"
    });

    sections.forEach(section => {
        scrollObserver.observe(section);
    });
}