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

  /* HTMX events: restore tabs after swap */
  document.body.addEventListener("htmx:afterSwap", () => {
    document.querySelectorAll("[data-tabs]").forEach(initTabs);
  });
})();
