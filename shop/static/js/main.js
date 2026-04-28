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
    clearTimeout(input._qtyTimer);
    input._qtyTimer = setTimeout(() => {
      input.dispatchEvent(new Event("change", { bubbles: true }));
    }, 300);
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

  /* HTMX: inject CSRF token into every non-GET request */
  const getCsrfToken = () =>
    document.cookie
      .split(";")
      .find((c) => c.trim().startsWith("csrftoken="))
      ?.split("=")[1] ?? "";

  document.body.addEventListener("htmx:configRequest", (evt) => {
    if (evt.detail.verb !== "get") {
      evt.detail.headers["X-CSRFToken"] = getCsrfToken();
    }
  });

  /* HTMX: cart toast notification */
  const showCartToast = (msg) => {
    const toast = document.getElementById("cart-toast");
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("cart-toast--visible");
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove("cart-toast--visible"), 2500);
  };

  /* Cart button pulse on click */
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-cart-btn]");
    if (!btn) return;
    btn.classList.remove("btn--cart-pulse");
    void btn.offsetWidth; // reflow to restart animation
    btn.classList.add("btn--cart-pulse");
    btn.addEventListener("animationend", () => btn.classList.remove("btn--cart-pulse"), { once: true });
  });

  /* Toggle button active state (wishlist / compare) */
  const WISHLIST_LABELS = { active: "\u2665 \u0412 \u0437\u0430\u043a\u043b\u0430\u0434\u043a\u0430\u0445", inactive: "\u2661 \u0412 \u0437\u0430\u043a\u043b\u0430\u0434\u043a\u0438" };
  const COMPARE_LABELS  = { active: "\u21C4 \u041f\u043e\u0440\u0456\u0432\u043d\u044e\u0454\u0442\u044c\u0441\u044f",  inactive: "\u21C4 \u041f\u043e\u0440\u0456\u0432\u043d\u044f\u0442\u0438" };

  document.body.addEventListener("htmx:afterRequest", (evt) => {
    const url  = evt.detail.requestConfig?.path ?? "";
    const verb = evt.detail.requestConfig?.verb ?? "";
    const ok   = evt.detail.successful;

    if (ok && verb === "post" && /\/cart\/add\//.test(url)) {
      showCartToast("Товар додано до кошика");
    }

    if (ok && verb === "post" && /\/wishlist\//.test(url)) {
      const btn = document.querySelector("[data-toggle-btn='wishlist']");
      if (!btn) return;
      const isActive = btn.classList.toggle("btn--active");
      const icon  = btn.querySelector("[data-toggle-icon]");
      const label = btn.querySelector("[data-toggle-label]");
      if (icon)  icon.textContent  = isActive ? "\u2665" : "\u2661";
      if (label) label.textContent = isActive ? "\u0412 \u0437\u0430\u043a\u043b\u0430\u0434\u043a\u0430\u0445" : "\u0412 \u0437\u0430\u043a\u043b\u0430\u0434\u043a\u0438";
      if (isActive) {
        btn.classList.remove("btn--heart-pulse");
        void btn.offsetWidth;
        btn.classList.add("btn--heart-pulse");
        btn.addEventListener("animationend", () => btn.classList.remove("btn--heart-pulse"), { once: true });
      }
    }

    if (ok && verb === "post" && /\/compare\//.test(url)) {
      const btn = document.querySelector("[data-toggle-btn='compare']");
      if (!btn) return;
      btn.classList.toggle("btn--active");
      const label = btn.querySelector("[data-toggle-label]");
      if (label) label.textContent = btn.classList.contains("btn--active")
        ? "\u041f\u043e\u0440\u0456\u0432\u043d\u044e\u0454\u0442\u044c\u0441\u044f"
        : "\u041f\u043e\u0440\u0456\u0432\u043d\u044f\u0442\u0438";
    }
  });

  /* HTMX events: restore tabs after swap */
  document.body.addEventListener("htmx:afterSwap", () => {
    document.querySelectorAll("[data-tabs]").forEach(initTabs);
  });
})();
