(() => {
  const hero = document.querySelector("[data-home-hero]");
  const canvas = document.querySelector("[data-home-hero-canvas]");
  if (!hero || !canvas) return;

  const frameCount = Number.parseInt(canvas.dataset.frameCount || "0", 10);
  const frameBase = canvas.dataset.frameBase || "";
  const framePrefix = canvas.dataset.framePrefix || "";
  const frameExt = canvas.dataset.frameExt || ".jpg";
  const framePad = Number.parseInt(canvas.dataset.framePad || "3", 10);
  if (!frameCount || !frameBase) return;

  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  function initScrollReveals() {
    const revealTargets = document.querySelectorAll("[data-reveal]");
    if (!revealTargets.length) return;

    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
      revealTargets.forEach((target) => target.classList.add("is-visible"));
      return;
    }

    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        });
      },
      {
        threshold: 0.16,
        rootMargin: "0px 0px -9% 0px",
      }
    );

    revealTargets.forEach((target) => revealObserver.observe(target));
  }

  let rafPending = false;
  let heroStart = 0;
  let heroTrackLength = 1;
  let latestScrollY = window.scrollY || 0;
  let currentIndex = 0;
  let lastDrawnIndex = -1;

  const frames = new Array(frameCount);
  let inFlight = 0;
  let nextToLoad = 0;
  const CONCURRENCY = 8;

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function devicePixelRatio() {
    return Math.max(1, window.devicePixelRatio || 1);
  }

  function urlFor(index) {
    const frameNumber = String(index + 1).padStart(framePad, "0");
    return `${frameBase}${framePrefix}${frameNumber}${frameExt}`;
  }

  function measureHeroTrack() {
    const rect = hero.getBoundingClientRect();
    heroStart = (window.scrollY || 0) + rect.top;
    const end = heroStart + hero.offsetHeight - window.innerHeight;
    heroTrackLength = Math.max(1, end - heroStart);
  }

  function syncCanvasSize() {
    const width = Math.max(1, Math.round(canvas.clientWidth * devicePixelRatio()));
    const height = Math.max(
      1,
      Math.round(canvas.clientHeight * devicePixelRatio())
    );
    if (canvas.width === width && canvas.height === height) return false;
    canvas.width = width;
    canvas.height = height;
    return true;
  }

  function drawCover(img) {
    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;
    const imageRatio = img.naturalWidth / img.naturalHeight;
    const canvasRatio = canvasWidth / canvasHeight;

    let drawWidth;
    let drawHeight;
    if (imageRatio > canvasRatio) {
      drawHeight = canvasHeight;
      drawWidth = canvasHeight * imageRatio;
    } else {
      drawWidth = canvasWidth;
      drawHeight = canvasWidth / imageRatio;
    }

    const drawX = (canvasWidth - drawWidth) / 2;
    const drawY = (canvasHeight - drawHeight) / 2;

    ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    ctx.drawImage(img, drawX, drawY, drawWidth, drawHeight);
  }

  function drawFrame(index, force) {
    const frame = frames[index];
    if (!frame || !frame.complete || !frame.naturalWidth) return;
    if (!force && lastDrawnIndex === index) return;
    drawCover(frame);
    lastDrawnIndex = index;
  }

  function updateFrameFromScroll() {
    if (prefersReducedMotion) {
      currentIndex = 0;
      return;
    }
    const progress = clamp((latestScrollY - heroStart) / heroTrackLength, 0, 1);
    currentIndex = Math.min(frameCount - 1, Math.floor(progress * frameCount));
  }

  function renderFrame() {
    rafPending = false;
    drawFrame(currentIndex, false);
  }

  function requestTick() {
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(renderFrame);
  }

  function loadNextBatch() {
    while (inFlight < CONCURRENCY && nextToLoad < frameCount) {
      const index = nextToLoad++;
      const img = new Image();
      img.decoding = "async";
      if (index === 0) {
        img.fetchPriority = "high";
      }

      img.onload = () => {
        inFlight -= 1;
        if (index === 0) {
          drawFrame(0, true);
        }
        if (index === currentIndex) {
          requestTick();
        }
        loadNextBatch();
      };

      img.onerror = () => {
        inFlight -= 1;
        loadNextBatch();
      };

      frames[index] = img;
      inFlight += 1;
      img.src = urlFor(index);
    }
  }

  function initialize() {
    syncCanvasSize();
    measureHeroTrack();
    latestScrollY = window.scrollY || 0;
    updateFrameFromScroll();
    requestTick();
    loadNextBatch();
  }

  initialize();
  initScrollReveals();

  if (!prefersReducedMotion) {
    window.addEventListener(
      "scroll",
      () => {
        latestScrollY = window.scrollY || 0;
        updateFrameFromScroll();
        requestTick();
      },
      { passive: true }
    );
  }

  window.addEventListener("resize", () => {
    const resized = syncCanvasSize();
    measureHeroTrack();
    latestScrollY = window.scrollY || 0;
    updateFrameFromScroll();
    drawFrame(currentIndex, resized);
    requestTick();
  });

  window.addEventListener("pageshow", () => {
    syncCanvasSize();
    measureHeroTrack();
    latestScrollY = window.scrollY || 0;
    updateFrameFromScroll();
    requestTick();
  });
})();
