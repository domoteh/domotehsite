(() => {
  "use strict";

  /* Tabs */
  const initTabs = (container) => {
    const btns = container.querySelectorAll("[data-tab-btn]");
    const panels = container.querySelectorAll("[data-tab-panel]");
    btns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const target = btn.dataset.tabBtn;
        btns.forEach((b) => b.classList.remove("tabs__btn--active", "home-tabs__btn--active"));
        panels.forEach((p) => p.classList.remove("tabs__panel--active"));
        btn.classList.add("tabs__btn--active", "home-tabs__btn--active");
        const panel = container.querySelector(`[data-tab-panel="${target}"]`);
        panel?.classList.add("tabs__panel--active");
      });
    });
  };

  document.querySelectorAll("[data-tabs]").forEach(initTabs);

  /* Quantity +/- */
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-qty-btn]");
    if (!btn) return;
    const wrap = btn.closest("[data-qty]");
    const input = wrap?.querySelector("input");
    if (!input) return;
    let val = parseInt(input.value, 10) || 1;
    if (btn.dataset.qtyBtn === "plus") val++;
    if (btn.dataset.qtyBtn === "minus" && val > 1) val--;
    input.value = val;
  });

  /* Mobile menu toggle */
  document.querySelector("[data-mobile-toggle]")?.addEventListener("click", () => {
    document.querySelector("[data-nav-inner]")?.classList.toggle("nav__inner--open");
  });

  /* Mobile subcategory toggle */
  document.querySelectorAll("[data-nav-item]").forEach((item) => {
    const link = item.querySelector(".nav__link");
    const menu = item.querySelector(".mega-menu");
    if (!menu) return;
    link.addEventListener("click", (e) => {
      if (window.innerWidth < 1025 || "ontouchstart" in window) {
        e.preventDefault();
        const opening = !item.classList.contains("nav__item--open");
        document.querySelectorAll("[data-nav-item]").forEach((other) => {
          other.classList.remove("nav__item--open");
        });
        if (opening) item.classList.add("nav__item--open");
      }
    });
  });

  /* Product gallery */
  document.addEventListener("click", (e) => {
    const thumb = e.target.closest("[data-gallery-thumb]");
    if (!thumb) return;
    const src = thumb.dataset.galleryThumb;
    const main = document.querySelector("[data-gallery-main] img");
    if (main) main.src = src;
    thumb.closest(".product-gallery__thumbs")
      ?.querySelectorAll(".product-gallery__thumb")
      .forEach((t) => t.classList.remove("product-gallery__thumb--active"));
    thumb.classList.add("product-gallery__thumb--active");
  });

  /* Nav scroll arrows */
  const navInner = document.querySelector("[data-nav-inner]");
  if (navInner) {
    const btnPrev = document.querySelector("[data-nav-prev]");
    const btnNext = document.querySelector("[data-nav-next]");
    const step = () => Math.round(navInner.clientWidth * 0.75);

    const updateNavArrows = () => {
      if (!btnPrev || !btnNext) return;
      const scrollable = navInner.scrollWidth > navInner.clientWidth + 1;
      const atStart = navInner.scrollLeft <= 0;
      const atEnd = navInner.scrollLeft + navInner.clientWidth >= navInner.scrollWidth - 1;
      btnPrev.toggleAttribute("hidden", !scrollable || atStart);
      btnNext.toggleAttribute("hidden", !scrollable || atEnd);
    };

    btnPrev?.addEventListener("click", () => {
      navInner.scrollBy({ left: -step(), behavior: "smooth" });
    });
    btnNext?.addEventListener("click", () => {
      navInner.scrollBy({ left: step(), behavior: "smooth" });
    });

    navInner.addEventListener("scroll", updateNavArrows, { passive: true });
    window.addEventListener("load", updateNavArrows);

    if (typeof ResizeObserver !== "undefined") {
      new ResizeObserver(updateNavArrows).observe(navInner);
    }
  }

  /* HTMX events: restore tabs after swap */
  document.body.addEventListener("htmx:afterSwap", () => {
    document.querySelectorAll("[data-tabs]").forEach(initTabs);
  });
})();
