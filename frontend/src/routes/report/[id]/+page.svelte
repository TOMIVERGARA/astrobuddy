<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { browser } from "$app/environment";
  import { API_URL } from "$lib/config";
  import { Button } from "$lib/components/ui/button";
  import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
  } from "$lib/components/ui/card";
  import { Skeleton } from "$lib/components/ui/skeleton";
  import * as HoverCard from "$lib/components/ui/hover-card";
  import { CheckCircle2, ArrowRight, XCircle } from "lucide-svelte";

  let reportId = $page.params.id;
  let loading = true;
  let error: string | null = null;
  let reportData: any = null;
  let mapElement: HTMLElement;
  let hoverMap: any = null;
  let hoverMarker: any = null;
  let leaflet: any = null;
  let isHoverOpen = false;

  // Helper functions
  function getCloudCoverIcon(clouds: number): string {
    if (clouds < 20) return "/cloudcover/clear.svg";
    if (clouds < 50) return "/cloudcover/mostlyclear.svg";
    if (clouds < 80) return "/cloudcover/partlycloudy.svg";
    return "/cloudcover/cloudy.svg";
  }

  function getPlanetImage(planetName: string): string {
    const name = planetName.toLowerCase();
    return `/planets/${name}.png`;
  }

  async function initHoverMap() {
    if (!browser || !mapElement || !reportData || hoverMap) return;

    if (!leaflet) {
      leaflet = (await import("leaflet")).default;
    }

    const customIcon = leaflet.divIcon({
      className: "astro-map-marker",
      html: '<div class="astro-map-marker-inner"></div>',
      iconSize: [24, 36],
      iconAnchor: [12, 34],
    });

    hoverMap = leaflet
      .map(mapElement, {
        zoomControl: false,
        attributionControl: false,
      })
      .setView([reportData.location.lat, reportData.location.lon], 10);

    leaflet
      .tileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        {
          subdomains: "abcd",
          maxZoom: 19,
        },
      )
      .addTo(hoverMap);

    hoverMarker = leaflet
      .marker([reportData.location.lat, reportData.location.lon], {
        icon: customIcon,
      })
      .addTo(hoverMap);

    // Pequeño delay para que el mapa se renderice correctamente
    setTimeout(() => {
      hoverMap?.invalidateSize();
    }, 100);
  }

  function zoomInHover() {
    if (hoverMap) hoverMap.zoomIn();
  }

  function zoomOutHover() {
    if (hoverMap) hoverMap.zoomOut();
  }

  function handleHoverOpen() {
    isHoverOpen = true;
    setTimeout(initHoverMap, 50);
  }

  function handleHoverClose() {
    isHoverOpen = false;
    if (hoverMap) {
      hoverMap.remove();
      hoverMap = null;
      hoverMarker = null;
    }
  }

  onMount(async () => {
    try {
      const response = await fetch(`${API_URL}/reports/${reportId}`);
      if (!response.ok) {
        throw new Error("report not found");
      }
      reportData = await response.json();
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  async function downloadPdf() {
    if (!reportData?.pdf_filename) return;

    try {
      const response = await fetch(
        `${API_URL}/download-pdf/${reportData.pdf_filename}`,
      );
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "observation_plan.pdf";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Error downloading PDF:", e);
    }
  }
</script>

<div
  class="min-h-screen text-foreground py-12 px-6 font-sans selection:bg-accent selection:text-accent-foreground relative z-10"
>
  <!-- Overlay when hover card is open -->
  {#if isHoverOpen}
    <div
      class="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm pointer-events-none"
    />
  {/if}
  {#if loading}
    <div class="max-w-7xl mx-auto space-y-6">
      <Skeleton class="h-12 w-64" />
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each Array(6) as _}
          <Skeleton class="h-48" />
        {/each}
      </div>
    </div>
  {:else if error}
    <div class="max-w-3xl mx-auto">
      <Card class="border border-red-500/20 bg-neutral-900/60">
        <CardHeader>
          <CardTitle class="text-red-500">error</CardTitle>
          <CardDescription class="pb-5">{error}</CardDescription>
        </CardHeader>
      </Card>
    </div>
  {:else if reportData}
    <div class="max-w-7xl mx-auto space-y-8">
      <!-- Header -->
      <div
        class="flex flex-col md:flex-row md:items-center md:justify-between gap-4"
      >
        <div class="flex items-center gap-4">
          <a
            href="/"
            class="text-muted-foreground hover:text-foreground transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="m12 19-7-7 7-7" />
              <path d="M19 12H5" />
            </svg>
          </a>
          <div>
            <h1 class="text-4xl font-bold tracking-tight lowercase mb-2">
              observation report
            </h1>
            <p class="text-muted-foreground lowercase">
              {new Date(reportData.generated_at).toLocaleDateString("en-US", {
                weekday: "long",
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </p>
          </div>
        </div>
        <Button on:click={downloadPdf} class="lowercase w-full md:w-auto">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="mr-2"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" x2="12" y1="15" y2="3" />
          </svg>
          download pdf
        </Button>
      </div>

      <!-- Bento Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Location & Date -->
        <Card
          class="border border-white/10 bg-neutral-900/60 shadow-lg md:col-span-1 md:row-span-2"
        >
          <CardHeader>
            <CardTitle class="lowercase text-lg">location & date</CardTitle>
          </CardHeader>
          <CardContent class="space-y-3">
            <div>
              <p class="text-sm text-muted-foreground lowercase">coordinates</p>
              <HoverCard.Root
                openDelay={200}
                closeDelay={100}
                onOpenChange={(open) =>
                  open ? handleHoverOpen() : handleHoverClose()}
              >
                <HoverCard.Trigger
                  class="font-mono text-sm cursor-help hover:text-green-400 transition-colors"
                >
                  {reportData.location.lat.toFixed(4)}, {reportData.location.lon.toFixed(
                    4,
                  )}
                </HoverCard.Trigger>
                <HoverCard.Content
                  side="right"
                  class="w-96 h-80 p-0 border-white/10 bg-neutral-900/95 backdrop-blur-sm overflow-hidden z-50"
                >
                  <div class="w-full h-full relative">
                    <div
                      bind:this={mapElement}
                      class="w-full h-full bg-black"
                    ></div>
                    <!-- Custom Zoom Controls -->
                    <div class="absolute bottom-4 right-4 z-[400]">
                      <div
                        class="flex flex-col rounded-md overflow-hidden shadow-lg border border-white/10 bg-black/70 backdrop-blur-sm"
                      >
                        <button
                          type="button"
                          class="px-3 py-2 text-lg font-semibold text-white hover:bg-white/10 transition-colors"
                          on:click={zoomInHover}
                        >
                          +
                        </button>
                        <div class="h-px bg-white/10"></div>
                        <button
                          type="button"
                          class="px-3 py-2 text-lg font-semibold text-white hover:bg-white/10 transition-colors"
                          on:click={zoomOutHover}
                        >
                          −
                        </button>
                      </div>
                    </div>
                  </div>
                </HoverCard.Content>
              </HoverCard.Root>
            </div>
            <div>
              <p class="text-sm text-muted-foreground lowercase">
                observation date
              </p>
              <p class="text-sm">{reportData.date}</p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground lowercase">timezone</p>
              <p class="text-sm">{reportData.timezone}</p>
            </div>
          </CardContent>
        </Card>

        <!-- Darkness Window -->
        {#if reportData.astro?.darkness_window}
          <Card
            class="border border-white/10 bg-neutral-900/60 shadow-lg md:col-span-1 md:row-span-2"
          >
            <CardHeader>
              <CardTitle class="lowercase text-lg">darkness window</CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="border-t border-white/10 pt-3">
                <p class="text-xs text-muted-foreground lowercase mb-2">
                  astronomical darkness
                </p>
                <p
                  class="text-2xl font-bold font-mono text-center flex justify-center items-center gap-2"
                >
                  {new Date(
                    reportData.astro.darkness_window.start,
                  ).toLocaleTimeString("es", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                  <ArrowRight />
                  {new Date(
                    reportData.astro.darkness_window.end,
                  ).toLocaleTimeString("es", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
              {#if reportData.astro.sun}
                <div class="border-t border-white/10 pt-3">
                  <div class="space-y-2">
                    <div class="flex justify-between items-center">
                      <span class="text-xs text-muted-foreground">sunset</span>
                      <span class="font-mono text-sm">
                        {new Date(reportData.astro.sun.set).toLocaleTimeString(
                          "es",
                          {
                            hour: "2-digit",
                            minute: "2-digit",
                          },
                        )}
                      </span>
                    </div>
                    <div class="flex justify-between items-center">
                      <span class="text-xs text-muted-foreground">sunrise</span>
                      <span class="font-mono text-sm">
                        {new Date(reportData.astro.sun.rise).toLocaleTimeString(
                          "es",
                          {
                            hour: "2-digit",
                            minute: "2-digit",
                          },
                        )}
                      </span>
                    </div>
                  </div>
                </div>
              {/if}
            </CardContent>
          </Card>
        {/if}

        <!-- AI Overview -->
        {#if reportData.ai?.overview}
          <Card
            class="border border-white/10 bg-neutral-900/60 shadow-lg md:col-span-2 md:row-span-2"
          >
            <CardHeader>
              <CardTitle class="lowercase text-lg">tonight's overview</CardTitle
              >
            </CardHeader>
            <CardContent>
              <p class="text-sm leading-relaxed">
                {reportData.ai.overview}
              </p>
            </CardContent>
          </Card>
        {/if}

        <!-- Moon Info -->
        {#if reportData.astro?.moon}
          <Card
            class="border border-white/10 bg-neutral-900/60 shadow-lg md:col-span-1 md:row-span-2"
          >
            <CardHeader>
              <CardTitle class="lowercase text-lg">moon</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="">
                {#if reportData.astro.moon.image_url}
                  <div class="flex-shrink-0">
                    <img
                      src={reportData.astro.moon.image_url}
                      alt="Moon phase"
                      class="w-48 rounded-full mx-auto mb-4"
                    />
                  </div>
                {/if}
                <div
                  class="flex items-center justify-center divide-x divide-white/10"
                >
                  <div class="px-4 text-center">
                    <p class="text-xs text-muted-foreground lowercase">phase</p>
                    <p class="text-sm font-semibold">
                      {reportData.astro.moon.phase_name}
                    </p>
                  </div>
                  {#if reportData.astro.moon.age_days}
                    <div class="px-4 text-center">
                      <p class="text-xs text-muted-foreground lowercase">age</p>
                      <p class="text-sm font-semibold">
                        {reportData.astro.moon.age_days.toFixed(1)} days
                      </p>
                    </div>
                  {/if}
                  <div class="px-4 text-center">
                    <p class="text-xs text-muted-foreground lowercase">
                      illumination
                    </p>
                    <p class="text-sm font-semibold">
                      {reportData.astro.moon.illumination.toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        {/if}

        <!-- Weather Summary -->
        {#if reportData.weather?.summary}
          <Card
            class="border border-white/10 bg-neutral-900/60 shadow-lg md:col-span-3 md:row-span-2 overflow-hidden"
          >
            <CardHeader>
              <CardTitle class="lowercase text-lg">weather forecast</CardTitle>
            </CardHeader>
            <CardContent class="space-y-3">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div>
                  <p class="text-xs text-muted-foreground lowercase">
                    avg temperature
                  </p>
                  <p class="text-lg font-semibold">
                    {reportData.weather.summary.temp_avg?.toFixed(1)}°C
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted-foreground lowercase">
                    cloud cover
                  </p>
                  <p class="text-lg font-semibold">
                    {reportData.weather.summary.avg_cloud_cover?.toFixed(0)}%
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted-foreground lowercase">
                    humidity
                  </p>
                  <p class="text-lg font-semibold">
                    {reportData.weather.summary.humidity_avg?.toFixed(0)}%
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted-foreground lowercase">
                    wind speed
                  </p>
                  <p class="text-lg font-semibold">
                    {reportData.weather.hourly &&
                    reportData.weather.hourly.length > 0
                      ? (
                          reportData.weather.hourly.reduce(
                            (sum, h) => sum + h.wind,
                            0,
                          ) / reportData.weather.hourly.length
                        ).toFixed(1)
                      : "—"} km/h
                  </p>
                </div>
              </div>

              <!-- Hourly Forecast -->
              {#if reportData.weather.hourly && reportData.weather.hourly.length > 0}
                <div class="border-t border-white/10 pt-3">
                  <div
                    class="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2"
                  >
                    {#each reportData.weather.hourly as hour}
                      <div
                        class="flex flex-col items-center gap-1 p-2 rounded-lg bg-black/30 border border-white/5"
                      >
                        <p class="text-xs text-muted-foreground">
                          {hour.time}
                        </p>
                        <img
                          src={getCloudCoverIcon(hour.clouds)}
                          alt="Cloud cover"
                          class="w-16 h-16 invert"
                        />
                        <p class="text-base font-semibold">
                          {hour.temp}°
                        </p>
                        <div
                          class="text-xs text-muted-foreground space-y-0.5 w-full"
                        >
                          <div class="flex justify-between gap-1">
                            <span>☁️</span>
                            <span>{hour.clouds.toFixed(0)}%</span>
                          </div>
                          <div class="flex justify-between gap-1">
                            <span>💧</span>
                            <span>{hour.humidity.toFixed(0)}%</span>
                          </div>
                        </div>
                      </div>
                    {/each}
                  </div>
                </div>
              {/if}
            </CardContent>
          </Card>
        {/if}

        <!-- Planets -->
        {#if reportData.planets && reportData.planets.length > 0}
          <Card
            class="border border-white/10 bg-neutral-900/60 shadow-lg lg:col-span-4 md:row-span-2"
          >
            <CardHeader>
              <CardTitle class="lowercase text-lg">visible planets</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                {#each reportData.planets as planet}
                  <div
                    class="p-3 rounded-lg border border-white/5 bg-black/20 space-y-3"
                  >
                    <!-- Header: Nombre y Magnitud -->
                    <div class="border-b border-white/5 pb-2">
                      <p class="font-bold text-lg">{planet.name}</p>
                      {#if planet.magnitude}
                        <p class="text-xs text-muted-foreground">
                          mag {planet.magnitude.toFixed(1)}
                        </p>
                      {/if}
                    </div>

                    <!-- Contenido: Imagen y Datos -->
                    <div class="flex gap-4">
                      <div class="flex-shrink-0">
                        <img
                          src={getPlanetImage(planet.name)}
                          alt={planet.name}
                          class="w-24 h-24 rounded-full object-cover"
                          on:error={(e) => {
                            e.currentTarget.style.display = "none";
                            e.currentTarget.nextElementSibling?.classList.remove(
                              "hidden",
                            );
                          }}
                        />
                        <div
                          class="w-24 h-24 rounded-full bg-gradient-to-br from-orange-500 to-yellow-500 flex items-center justify-center text-3xl hidden"
                        >
                          🪐
                        </div>
                      </div>
                      <div class="flex-1 my-auto">
                        <div class="text-xs text-muted-foreground space-y-1">
                          {#if planet.distance_au}
                            <div class="flex justify-between">
                              <span>distance:</span>
                              <span class="text-foreground"
                                >{planet.distance_au.toFixed(2)} AU</span
                              >
                            </div>
                          {/if}
                          {#if planet.rise}
                            <div class="flex justify-between">
                              <span>rise:</span>
                              <span class="text-foreground font-mono">
                                {new Date(planet.rise).toLocaleTimeString(
                                  "en-US",
                                  {
                                    hour: "2-digit",
                                    minute: "2-digit",
                                  },
                                )}
                              </span>
                            </div>
                          {/if}
                          {#if planet.set}
                            <div class="flex justify-between">
                              <span>set:</span>
                              <span class="text-foreground font-mono">
                                {new Date(planet.set).toLocaleTimeString(
                                  "en-US",
                                  {
                                    hour: "2-digit",
                                    minute: "2-digit",
                                  },
                                )}
                              </span>
                            </div>
                          {/if}
                          {#if planet.is_visible !== undefined}
                            <div class="flex justify-between items-center">
                              <span>visible:</span>
                              <span class="text-foreground">
                                {#if planet.is_visible}
                                  <CheckCircle2
                                    class="inline-block w-4 h-4 text-green-400"
                                  />
                                {:else}
                                  <XCircle
                                    class="inline-block w-4 h-4 text-red-400"
                                  />
                                {/if}
                              </span>
                            </div>
                          {/if}
                        </div>
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
            </CardContent>
          </Card>
        {/if}

        <!-- Deep Sky Objects -->
        {#if reportData.ai?.objects && reportData.ai.objects.length > 0}
          <Card
            class="border border-white/10 bg-neutral-900/60 shadow-lg lg:col-span-4 md:row-span-4"
          >
            <CardHeader>
              <CardTitle class="lowercase text-lg">
                recommended deep sky objects
              </CardTitle>
              <CardDescription class="lowercase">
                {reportData.ai.objects.length} objects selected for your session
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                {#each reportData.ai.objects as obj}
                  <div
                    class="p-3 rounded-lg border border-white/10 bg-black/30 space-y-2 hover:border-white/20 transition-colors"
                  >
                    <!-- Header -->
                    <div class="space-y-1">
                      <div class="flex items-start justify-between">
                        <div>
                          <span class="text-xs text-muted-foreground">#</span>
                          <span
                            class="text-2xl font-bold text-transparent bg-clip-text bg-green-400"
                          >
                            {obj.ranking}
                          </span>
                          <h3 class="font-bold text-2xl mt-1">
                            {obj.id}
                          </h3>
                        </div>
                        {#if obj.mag}
                          <span
                            class="text-xs px-2 py-1 rounded-none bg-white/10 font-mono"
                          >
                            mag {obj.mag}
                          </span>
                        {/if}
                      </div>
                      {#if obj.name}
                        <p class="text-sm text-muted-foreground">
                          {obj.name}
                        </p>
                      {/if}
                      <p class="text-xs text-muted-foreground">
                        {obj.type}
                        {#if obj.constellation}
                          • {obj.constellation}{/if}
                        {#if obj.size}
                          • {obj.size}{/if}
                      </p>
                    </div>

                    <!-- Schedule -->
                    <div
                      class="grid grid-cols-3 gap-2 text-xs border-t border-white/5 pt-3"
                    >
                      <div>
                        <p class="text-muted-foreground lowercase">rise</p>
                        <p class="font-mono">
                          {obj.rise
                            ? new Date(obj.rise).toLocaleTimeString("en-US", {
                                hour: "2-digit",
                                minute: "2-digit",
                              })
                            : "—"}
                        </p>
                      </div>
                      <div>
                        <p class="text-muted-foreground lowercase">transit</p>
                        <p class="font-mono">
                          {obj.transit
                            ? new Date(obj.transit).toLocaleTimeString(
                                "en-US",
                                { hour: "2-digit", minute: "2-digit" },
                              )
                            : "—"}
                          {#if obj.transit_altitude}
                            <span class="text-muted-foreground">
                              ({obj.transit_altitude}°)
                            </span>
                          {/if}
                        </p>
                      </div>
                      <div>
                        <p class="text-muted-foreground lowercase">set</p>
                        <p class="font-mono">
                          {obj.set
                            ? new Date(obj.set).toLocaleTimeString("en-US", {
                                hour: "2-digit",
                                minute: "2-digit",
                              })
                            : "—"}
                        </p>
                      </div>
                    </div>

                    <!-- Description -->
                    {#if obj.description}
                      <div
                        class="text-sm text-muted-foreground border-t border-white/5 pt-3"
                      >
                        <p>{obj.description}</p>
                      </div>
                    {/if}

                    <!-- Tips & Facts -->
                    <div class="space-y-2 border-t border-white/5 pt-3">
                      {#if obj.tips}
                        <div
                          class="text-sm p-2 bg-green-400/10 border border-green-400/20"
                        >
                          <p
                            class="text-xs text-green-300 lowercase font-semibold mb-1"
                          >
                            tips
                          </p>
                          <p class="text-sm">{obj.tips}</p>
                        </div>
                      {/if}
                      {#if obj.fact}
                        <div
                          class="text-sm p-2 bg-purple-500/10 border border-purple-500/20"
                        >
                          <p
                            class="text-xs text-purple-300 lowercase font-semibold mb-1"
                          >
                            fact
                          </p>
                          <p class="text-sm">{obj.fact}</p>
                        </div>
                      {/if}
                    </div>
                  </div>
                {/each}
              </div>
            </CardContent>
          </Card>
        {/if}
      </div>
    </div>
  {/if}
</div>

<!-- Leaflet CSS -->
<svelte:head>
  <link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
    crossorigin=""
  />
</svelte:head>

<style>
  /* Prevent white flash on map load */
  :global(.leaflet-container) {
    background: #000 !important;
  }

  :global(.leaflet-tile-pane) {
    filter: grayscale(100%) contrast(110%);
    background: #000;
  }

  :global(.leaflet-pane) {
    background: transparent;
  }

  :global(.leaflet-tile) {
    background: #000;
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
