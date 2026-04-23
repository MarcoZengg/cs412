(() => {
  const STEPPER_SELECTOR = ".session-stepper";
  const ACTIVE_SELECTOR =
    "[aria-current='step'], .session-stepper__dot--active, .session-stepper__subdot--active";

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function centerElement(stepper, element, behavior = "auto") {
    if (!stepper || !element) return;

    const viewportRect = stepper.getBoundingClientRect();
    const elementRect = element.getBoundingClientRect();
    const delta =
      elementRect.left +
      elementRect.width / 2 -
      (viewportRect.left + viewportRect.width / 2);
    const maxScrollLeft = Math.max(0, stepper.scrollWidth - stepper.clientWidth);
    const target = clamp(stepper.scrollLeft + delta, 0, maxScrollLeft);

    // Safari can ignore inline centering in scrollIntoView; explicit scroll math is reliable.
    stepper.scrollTo({ left: target, behavior });
  }

  function centerCurrentStep(stepper, behavior = "auto") {
    const current = stepper.querySelector(ACTIVE_SELECTOR);
    if (!current) return;
    centerElement(stepper, current, behavior);
  }

  function installStepper(stepper) {
    centerCurrentStep(stepper, "auto");

    stepper.addEventListener("click", (event) => {
      const hit = event.target.closest(
        ".session-stepper__dot, .session-stepper__subdot"
      );
      if (!hit || !stepper.contains(hit)) return;
      requestAnimationFrame(() => centerElement(stepper, hit, "smooth"));
    });
  }

  function init() {
    const steppers = document.querySelectorAll(STEPPER_SELECTOR);
    if (!steppers.length) return;

    steppers.forEach(installStepper);

    let resizeTimer = null;
    window.addEventListener("resize", () => {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(() => {
        steppers.forEach((stepper) => centerCurrentStep(stepper, "auto"));
      }, 120);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
