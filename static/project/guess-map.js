/*
 * File: guess-map.js
 * Description: Render the Submit-Guess page map + Street View panorama.
 *   Clicking the map fills #id_guess_latitude / #id_guess_longitude and
 *   moves/creates the guess marker. If the round already has a saved
 *   guess it is restored on load. Street View is initialized for the
 *   round's true location.
 *
 * Previously inline in round_submit_form.html. Moved here because
 * data-* attributes on #guess-map-root carry all coordinates.
 *
 * Expected DOM (only rendered when google_maps_enabled is true):
 *   <div id="guess-map-root"
 *        data-default-lat data-default-lng
 *        [data-guess-lat] [data-guess-lng]>
 *     <gmp-map ...></gmp-map>
 *   </div>
 *   <div id="streetview-root"></div>
 *   <p id="streetview-status"></p>
 *   <input id="id_guess_latitude"> <input id="id_guess_longitude">
 *
 * Assumes the Google Maps JS API loader (see
 * project/includes/google_maps_head.html) has been included in <head>.
 */
(() => {
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

  async function initStreetView(streetViewRoot, streetViewStatus, target) {
    const sv = new google.maps.StreetViewService();
    try {
      const response = await sv.getPanorama({
        location: target,
        radius: 1000,
        source: google.maps.StreetViewSource.OUTDOOR,
      });
      const panoLocation = response?.data?.location?.latLng || target;
      new google.maps.StreetViewPanorama(streetViewRoot, {
        position: panoLocation,
        pov: { heading: 34, pitch: 5 },
        linksControl: true,
        panControl: true,
        addressControl: false,
        showRoadLabels: false,
        enableCloseButton: false,
      });
      if (streetViewStatus) streetViewStatus.textContent = "";
    } catch (_error) {
      if (streetViewStatus) {
        streetViewStatus.textContent =
          "No Street View panorama found near this location.";
      }
    }
  }

  function initGuessMap(inner, root, latInput, lngInput) {
    let guessMarker = null;
    const pinGuess = new google.maps.marker.PinElement(GUESS_PIN);

    function setGuess(lat, lng) {
      latInput.value = lat.toFixed(6);
      lngInput.value = lng.toFixed(6);

      const pos = { lat, lng };
      if (!guessMarker) {
        guessMarker = new google.maps.marker.AdvancedMarkerElement({
          map: inner,
          position: pos,
          title: "Your guess",
          content: pinGuess,
        });
      } else {
        guessMarker.position = pos;
      }
    }

    const existingLat = parseCoord(root.dataset.guessLat);
    const existingLng = parseCoord(root.dataset.guessLng);
    if (existingLat !== null && existingLng !== null) {
      setGuess(existingLat, existingLng);
      inner.setCenter({ lat: existingLat, lng: existingLng });
      inner.setZoom(8);
    }

    inner.addListener("click", (event) => {
      if (!event.latLng) return;
      setGuess(event.latLng.lat(), event.latLng.lng());
    });
  }

  window.addEventListener("load", async () => {
    const root = document.getElementById("guess-map-root");
    if (!root || !window.google?.maps) return;

    const streetViewRoot = document.getElementById("streetview-root");
    const streetViewStatus = document.getElementById("streetview-status");
    const latInput = document.getElementById("id_guess_latitude");
    const lngInput = document.getElementById("id_guess_longitude");

    await google.maps.importLibrary("maps");
    await google.maps.importLibrary("marker");

    const inner = await waitForInnerMap(root.querySelector("gmp-map"));
    if (!inner) return;

    if (latInput && lngInput) {
      initGuessMap(inner, root, latInput, lngInput);
    }

    if (streetViewRoot) {
      const defaultLat = parseCoord(root.dataset.defaultLat);
      const defaultLng = parseCoord(root.dataset.defaultLng);
      if (defaultLat !== null && defaultLng !== null) {
        initStreetView(streetViewRoot, streetViewStatus, {
          lat: defaultLat,
          lng: defaultLng,
        });
      }
    }
  });
})();
