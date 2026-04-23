/*
 * File: card-nav.js
 * Description: Expand/collapse the card-style primary navigation.
 * - Click/keyboard always toggles (works on touch and desktop).
 * - Pointer-capable devices also open on hover, close on pointer leave.
 * - Height is recomputed in requestAnimationFrame; resize is debounced.
 */
(() => {
  const nav = document.querySelector("[data-card-nav]");
  if (!nav) return;

  const toggle = nav.querySelector("[data-card-nav-toggle]");
  const content = nav.querySelector(".card-nav-content");
  const top = nav.querySelector(".card-nav-top");
  if (!toggle || !content || !top) return;

  const EXPANDED_PADDING = 14;
  let expanded = false;
  let heightRafPending = false;

  function measureExpandedHeight() {
    return top.offsetHeight + content.scrollHeight + EXPANDED_PADDING;
  }

  function applyHeight() {
    heightRafPending = false;
    nav.style.height = expanded
      ? `${measureExpandedHeight()}px`
      : `${top.offsetHeight}px`;
  }

  function scheduleHeight() {
    if (heightRafPending) return;
    heightRafPending = true;
    requestAnimationFrame(applyHeight);
  }

  function setExpanded(next) {
    if (next === expanded) return;
    expanded = next;
    nav.classList.toggle("open", expanded);
    toggle.classList.toggle("open", expanded);
    toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
    toggle.setAttribute("aria-label", expanded ? "Close menu" : "Open menu");
    content.setAttribute("aria-hidden", expanded ? "false" : "true");
    scheduleHeight();
  }

  function toggleMenu() {
    setExpanded(!expanded);
  }

  // Hover-to-open only on pointer-capable devices. Pointer events work in
  // every modern browser (including Safari 14+); the old mouseover fallback
  // was redundant with pointerenter and caused duplicate setExpanded() calls.
  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    const openOnHover = () => setExpanded(true);
    const closeOnHover = () => setExpanded(false);
    toggle.addEventListener("pointerenter", openOnHover);
    nav.addEventListener("pointerenter", openOnHover);
    nav.addEventListener("pointerleave", closeOnHover);
  }

  toggle.addEventListener("click", toggleMenu);
  toggle.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      toggleMenu();
    }
  });

  // Debounce resize: recompute once after the window stops changing.
  let resizeTimer = 0;
  window.addEventListener("resize", () => {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(scheduleHeight, 120);
  });

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && expanded) setExpanded(false);
  });

  // Initial state: ensure aria + height are in sync without toggling classes.
  applyHeight();
})();
