/*
 * File: countup.js
 * Description: Shared count-up animation for any element marked with
 *   [data-countup]. Reads data-countup-from, data-countup-to, and
 *   data-countup-duration (seconds). Starts once the element is visible.
 *
 * Previously duplicated inline in round_detail.html and
 * gamesession_detail.html; extracted here so both pages (and any future
 * ones) share a single implementation and a single IntersectionObserver.
 */
(() => {
  const counters = document.querySelectorAll("[data-countup]");
  if (!counters.length) return;

  const easeOut = (t) => 1 - Math.pow(1 - t, 3);

  function animateCounter(counter) {
    const toRaw = Number(counter.dataset.countupTo);
    const fromRaw = Number(counter.dataset.countupFrom || 0);
    const durationSec = Number(counter.dataset.countupDuration || 2);
    if (!Number.isFinite(toRaw) || !Number.isFinite(fromRaw)) return;

    const durationMs = Math.max(100, durationSec * 1000);
    const decimals = Math.max(
      ((counter.dataset.countupTo || "").split(".")[1] || "").length,
      ((counter.dataset.countupFrom || "").split(".")[1] || "").length
    );
    const format = (value) =>
      new Intl.NumberFormat("en-US", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      }).format(value);

    counter.textContent = format(fromRaw);

    const start = performance.now();
    const delta = toRaw - fromRaw;
    const tick = (now) => {
      const t = Math.min((now - start) / durationMs, 1);
      counter.textContent = format(fromRaw + delta * easeOut(t));
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.4 }
  );

  counters.forEach((el) => observer.observe(el));
})();
