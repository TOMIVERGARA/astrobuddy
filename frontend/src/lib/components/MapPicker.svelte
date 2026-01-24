<script lang="ts">
  import { onMount, createEventDispatcher } from "svelte";
  import { browser } from "$app/environment";

  export let lat: number = -34.6037; // Default Buenos Aires
  export let lon: number = -58.3816;

  const dispatch = createEventDispatcher();

  let mapElement: HTMLElement;
  let map: any;
  let marker: any;
  let leaflet: any;

  // Search State
  let searchQuery = "";
  let searchResults: any[] = [];
  let isSearching = false;
  let searchMode: "location" | "coords" = "location"; // Tab state
  let inputLat = lat.toString();
  let inputLon = lon.toString();

  // Debounce search
  let searchTimeout: any;

  async function handleSearchInput() {
    if (!searchQuery || searchQuery.length < 3) {
      searchResults = [];
      return;
    }

    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
      isSearching = true;
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}`,
        );
        if (response.ok) {
          searchResults = await response.json();
        }
      } catch (error) {
        console.error("Search failed", error);
      } finally {
        isSearching = false;
      }
    }, 500);
  }

  function selectLocation(result: any) {
    const newLat = parseFloat(result.lat);
    const newLon = parseFloat(result.lon);
    updateMap(newLat, newLon);
    searchQuery = result.display_name;
    searchResults = [];
  }

  function handleCoordsSubmit() {
    const newLat = parseFloat(inputLat);
    const newLon = parseFloat(inputLon);
    if (!isNaN(newLat) && !isNaN(newLon)) {
      updateMap(newLat, newLon);
    }
  }

  function updateMap(newLat: number, newLon: number) {
    lat = newLat;
    lon = newLon;
    inputLat = lat.toFixed(6);
    inputLon = lon.toFixed(6);

    if (map && leaflet) {
      map.flyTo([lat, lon], 10);
      marker.setLatLng([lat, lon]);
    }
    dispatch("change", { lat, lon });
  }

  function zoomIn() {
    if (map) {
      map.zoomIn();
    }
  }

  function zoomOut() {
    if (map) {
      map.zoomOut();
    }
  }

  onMount(async () => {
    if (browser) {
      leaflet = (await import("leaflet")).default;

      const customIcon = leaflet.divIcon({
        className: "astro-map-marker",
        html: '<div class="astro-map-marker-inner"></div>',
        iconSize: [24, 36],
        iconAnchor: [12, 34],
      });

      map = leaflet
        .map(mapElement, {
          zoomControl: false,
          attributionControl: false,
        })
        .setView([lat, lon], 4);

      leaflet
        .tileLayer(
          "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
          {
            subdomains: "abcd",
            maxZoom: 19,
          },
        )
        .addTo(map);

      marker = leaflet
        .marker([lat, lon], {
          draggable: true,
          icon: customIcon,
        })
        .addTo(map);

      marker.on("dragend", () => {
        const pos = marker.getLatLng();
        updateMap(pos.lat, pos.lng);
      });

      map.on("click", (e: any) => {
        const { lat: newLat, lng: newLng } = e.latlng;
        updateMap(newLat, newLng);
      });
    }
  });

  $: if (
    map &&
    marker &&
    (lat !== marker.getLatLng().lat || lon !== marker.getLatLng().lng)
  ) {
    marker.setLatLng([lat, lon]);
    map.setView([lat, lon], map.getZoom(), { animate: false }); // Prevent fighting with flyTo if possible, but keep reactive
  }
</script>

<div class="w-full h-full flex flex-col">
  <!-- Search Box Panel -->
  <div
    class="bg-black/80 backdrop-blur-md border border-white/10 p-1 shadow-2xl transition-all duration-300"
  >
    <!-- Tabs -->
    <div class="grid grid-cols-2 mb-1">
      <button
        class="py-2 text-xs font-bold uppercase tracking-wider transition-colors {searchMode ===
        'location'
          ? 'bg-white text-black'
          : 'text-zinc-500 hover:text-white'}"
        on:click={() => (searchMode = "location")}
      >
        Place
      </button>
      <button
        class="py-2 text-xs font-bold uppercase tracking-wider transition-colors {searchMode ===
        'coords'
          ? 'bg-white text-black'
          : 'text-zinc-500 hover:text-white'}"
        on:click={() => (searchMode = "coords")}
      >
        Coords
      </button>
    </div>

    <!-- Content -->
    <div class="relative">
      {#if searchMode === "location"}
        <input
          type="text"
          bind:value={searchQuery}
          on:input={handleSearchInput}
          placeholder="search city, country..."
          class="w-full bg-white/5 border border-white/10 text-white text-sm p-2 focus:outline-none focus:border-white/30"
        />

        {#if searchResults.length > 0}
          <ul
            class="absolute top-full left-0 right-0 max-h-48 overflow-y-auto bg-black border border-t-0 border-white/10 shadow-xl z-10"
          >
            {#each searchResults as result}
              <li>
                <button
                  class="w-full text-left p-3 text-xs text-zinc-300 hover:bg-white/10 hover:text-white transition-colors border-b border-white/5 last:border-0"
                  on:click={() => selectLocation(result)}
                >
                  {result.display_name}
                </button>
              </li>
            {/each}
          </ul>
        {/if}
      {:else}
        <div class="flex gap-1">
          <input
            type="text"
            bind:value={inputLat}
            placeholder="Lat"
            class="w-1/2 bg-white/5 border border-white/10 text-white text-sm p-2 focus:outline-none focus:border-white/30"
          />
          <input
            type="text"
            bind:value={inputLon}
            placeholder="Lon"
            class="w-1/2 bg-white/5 border border-white/10 text-white text-sm p-2 focus:outline-none focus:border-white/30"
          />
          <button
            on:click={handleCoordsSubmit}
            class="bg-white text-black px-3 font-bold text-xs uppercase"
          >
            go
          </button>
        </div>
      {/if}
    </div>
  </div>

  <!-- Map Container -->
  <div class="flex-1 relative group">
    <div bind:this={mapElement} class="w-full h-full bg-black"></div>

    <!-- Custom Zoom Controls -->
    <div class="absolute bottom-4 right-4 z-[400] pointer-events-none">
      <div
        class="flex flex-col rounded-md overflow-hidden shadow-lg border border-white/10 bg-black/70 backdrop-blur-sm pointer-events-auto"
      >
        <button
          type="button"
          class="px-3 py-2 text-lg font-semibold text-white hover:bg-white/10 transition-colors"
          on:click={zoomIn}
        >
          +
        </button>
        <div class="h-px bg-white/10"></div>
        <button
          type="button"
          class="px-3 py-2 text-lg font-semibold text-white hover:bg-white/10 transition-colors"
          on:click={zoomOut}
        >
          −
        </button>
      </div>
    </div>

    <!-- Styles for Leaflet inside -->
    <link
      rel="stylesheet"
      href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
      crossorigin=""
    />
  </div>
</div>

<style>
  /* Custom Scrollbar for results */
  ul::-webkit-scrollbar {
    width: 4px;
  }
  ul::-webkit-scrollbar-track {
    background: #000;
  }
  ul::-webkit-scrollbar-thumb {
    background: #333;
  }

  /* Invert map tiles for a truly dark mode if desired, otherwise standard dark tiles are fine. 
       This adds a subtle monochrome filter to the map tiles */
  :global(.leaflet-tile-pane) {
    filter: grayscale(100%) contrast(110%);
  }

  :global(.astro-map-marker) {
    background: transparent;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  :global(.astro-map-marker-inner) {
    position: relative;
    width: 18px;
    height: 18px;
    border-radius: 9999px;
    background-color: #4ade80;
    transform: translateY(2px);
  }

  :global(.astro-map-marker-inner::after) {
    /* Tail of the pin */
    content: "";
    position: absolute;
    top: 90%;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-style: solid;
    border-width: 6px 6px 0 6px;
    border-color: #4ade80 transparent transparent transparent;
  }

  :global(.astro-map-marker-inner::before) {
    /* Inner white circle */
    content: "";
    position: absolute;
    inset: 5px;
    border-radius: 9999px;
    background-color: #000;
  }
</style>
