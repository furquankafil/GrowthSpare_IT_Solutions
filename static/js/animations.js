/**
 * GrowthSpare IT Solutions - Core Interface Animation Suite
 * Employs GSAP (GreenSock Animation Platform) to handle page entrance timelines,
 * scroll-triggered card states, and dynamic micro-interactions.
 */

document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    // Initialize core animation sequences defensively
    initHeroEntrance();
    initCardHoverMicroInteractions();
    initStatsCountAnimations();
});

/**
 * Executes a premium entrance animation timeline for Hero structures.
 * Sequences typography transitions, button displays, and console card canvas slides.
 */
function initHeroEntrance() {
    // Prevent execution errors if the active page is not the primary homepage
    const heroTitle = document.querySelector("h1.font-poppins");
    if (!heroTitle || typeof gsap === "undefined") return;

    const tl = gsap.timeline({ defaults: { ease: "power4.out" } });

    // Entrance timeline mapping
    tl.fromTo(
        "header",
        { y: -100, opacity: 0 },
        { y: 0, opacity: 1, duration: 1.2 }
    )
    .fromTo(
        heroTitle,
        { y: 40, opacity: 0 },
        { y: 0, opacity: 1, duration: 1 },
        "-=0.6"
    )
    .fromTo(
        "#hero-typed-target",
        { opacity: 0 },
        { opacity: 1, duration: 0.8 },
        "-=0.4"
    )
    .fromTo(
        "p.text-slate-500",
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 1 },
        "-=0.6"
    )
    .fromTo(
        "a.bg-gradient-to-r, a.border-slate-900\\/10",
        { scale: 0.95, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.8, stagger: 0.15 },
        "-=0.5"
    )
    .fromTo(
        ".lg\\:col-span-5",
        { x: 50, opacity: 0 },
        { x: 0, opacity: 1, duration: 1.4 },
        "-=1"
    );
}

/**
 * Attaches smooth interactive mouse movements and scale alterations
 * to primary Glassmorphism cards across portfolio and services views.
 */
function initCardHoverMicroInteractions() {
    const cards = document.querySelectorAll(".glassmorphism");
    if (cards.length === 0 || typeof gsap === "undefined") return;

    cards.forEach(card => {
        card.addEventListener("mouseenter", () => {
            gsap.to(card, {
                y: -5,
                scale: 1.01,
                boxShadow: "0 20px 40px -15px rgba(37, 99, 235, 0.15)",
                duration: 0.4,
                ease: "power2.out"
            });
        });

        card.addEventListener("mouseleave", () => {
            gsap.to(card, {
                y: 0,
                scale: 1,
                boxShadow: "0 0px 0px 0px rgba(0,0,0,0)",
                duration: 0.4,
                ease: "power2.out"
            });
        });
    });
}

/**
 * Triggers interactive odometer-like ascending number counts on statistic values
 * using standard IntersectionObserver depth triggers.
 */
function initStatsCountAnimations() {
    const statElements = document.querySelectorAll("[data-target-stat]");
    if (statElements.length === 0 || typeof gsap === "undefined") return;

    const statsObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const targetValue = parseFloat(element.getAttribute("data-target-stat"));
                const decimalPlaces = element.getAttribute("data-decimals") || "0";
                
                const countObj = { value: 0 };
                
                gsap.to(countObj, {
                    value: targetValue,
                    duration: 2.2,
                    ease: "power2.out",
                    onUpdate: () => {
                        element.textContent = countObj.value.toFixed(parseInt(decimalPlaces)) + 
                            (element.getAttribute("data-suffix") || "");
                    }
                });

                observer.unobserve(element);
            }
        });
    }, {
        threshold: 0.5
    });

    statElements.forEach(elem => {
        statsObserver.observe(elem);
    });
}