/*
 * File: round-map.js
 * Description: Render the round-detail result map (actual location + optional
 *   guess marker + connecting polyline + auto-fit bounds).
 *
 * Previously inline in round_detail.html. Moved here because data-*
 * attributes on #round-map-root already carry all coordinates, so the
 * script needs no template variables.
 *
 * Expected DOM (only rendered when google_maps_enabled is true):
 *   <div id="round-map-root"
 *        data-actual-lat data-actual-lng
 *        [data-guess-lat] [data-guess-lng]>
 *     <gmp-map ...></gmp-map>
 *   </div>
 *
 * Assumes the Google Maps JS API loader (see
 * project/includes/google_maps_head.html) has been included in <head>.
 */
(() => {
  const ACTUAL_PIN = {
    background: "#4c9dff",
    borderColor: "#0f1419",
    glyphColor: "#fff",
  };
  const GUESS_PIN = {
    background: "#ff9f4c",
    borderColor: "#0f1419",
    glyphColor: "#0f1419",
  };

  function parseCoord(value) {
    if (value === undefined || value === "") return null;
    const parsed = parseFloat(value);
    return Number.isNaN(parsed) ? null : parsed;
  }

  async function waitForInnerMap(mapEl, attempts = 120) {
    let inner = mapEl?.innerMap;
    for (let i = 0; i < attempts && !inner; i++) {
      await new Promise((r) => requestAnimationFrame(r));
      inner = mapEl?.innerMap;
    }
    return inner || null;
  }

  function safePin(options) {
    try {
      return new google.maps.marker.PinElement(options);
    } catch {
      return null;
    }
  }

  window.addEventListener("load", async () => {
    const root = document.getElementById("round-map-root");
    if (!root || !window.google?.maps) return;

    const actualLat = parseCoord(root.dataset.actualLat);
    const actualLng = parseCoord(root.dataset.actualLng);
    if (actualLat === null || actualLng === null) return;

    const guessLat = parseCoord(root.dataset.guessLat);
    const guessLng = parseCoord(root.dataset.guessLng);
    const hasGuess = guessLat !== null && guessLng !== null;

    const { AdvancedMarkerElement } =
      await google.maps.importLibrary("marker");

    const inner = await waitForInnerMap(root.querySelector("gmp-map"));
    if (!inner) return;

    const actualPos = { lat: actualLat, lng: actualLng };
    const pinActual = safePin(ACTUAL_PIN);
    new AdvancedMarkerElement({
      map: inner,
      position: actualPos,
      title: "Actual location",
      ...(pinActual ? { content: pinActual } : {}),
    });

    if (!hasGuess) {
      inner.setCenter(actualPos);
      inner.setZoom(10);
      return;
    }

    const guessPos = { lat: guessLat, lng: guessLng };
    const pinGuess = safePin(GUESS_PIN);
    new AdvancedMarkerElement({
      map: inner,
      position: guessPos,
      title: "Your guess",
      ...(pinGuess ? { content: pinGuess } : {}),
    });

    new google.maps.Polyline({
      map: inner,
      path: [guessPos, actualPos],
      geodesic: false,
      strokeColor: "#ff3b3b",
      strokeOpacity: 0.95,
      strokeWeight: 3,
    });

    const bounds = new google.maps.LatLngBounds();
    bounds.extend(actualPos);
    bounds.extend(guessPos);
    inner.fitBounds(bounds, { top: 56, right: 56, bottom: 56, left: 56 });
  });
})();
