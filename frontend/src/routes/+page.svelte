<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import MapPicker from "$lib/components/MapPicker.svelte";
  import TelescopeInput from "$lib/components/TelescopeInput.svelte";
  import DatePicker from "$lib/components/DatePicker.svelte";
  import CatalogView from "$lib/components/CatalogView.svelte";
  import PastSessionsView from "$lib/components/PastSessionsView.svelte";
  import AboutView from "$lib/components/AboutView.svelte";
  import { Button } from "$lib/components/ui/button";
  import { Label } from "$lib/components/ui/label";
  import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
  } from "$lib/components/ui/card";
  import * as Tabs from "$lib/components/ui/tabs";
  import { MultiStepLoader } from "$lib/components/ui/multi-step-loader";
  import {
    ToggleGroup,
    ToggleGroupItem,
  } from "$lib/components/ui/toggle-group";
  import ChevronRight from "lucide-svelte/icons/chevron-right";
  import Clock from "lucide-svelte/icons/clock";
  import Info from "lucide-svelte/icons/info";
  import { fade } from "svelte/transition";
  import { quintOut } from "svelte/easing";
  import Separator from "$lib/components/ui/separator/separator.svelte";

  let lat = -34.6037;
  let lon = -58.3816;
  let date = new Date().toISOString().split("T")[0];
  let telescope = "";
  let language = "english";

  function handleTelescopeChange(event: CustomEvent<string>) {
    telescope = event.detail;
  }

  // Get user's current location on mount
  onMount(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          lat = position.coords.latitude;
          lon = position.coords.longitude;
        },
        (error) => {
          console.log(
            "Geolocation permission denied or unavailable, using default location",
          );
        },
      );
    }
  });

  let loading = false;
  let error: string | null = null;
  let generatedPdfUrl: string | null = null;
  let currentStep = 0;

  // Past sessions state
  let showPastSessions = false;
  let showAbout = false;

  const loadingStates = [
    { text: "initializing observation session..." },
    { text: "calculating astronomical darkness window..." },
    { text: "fetching hourly weather forecast..." },
    { text: "calculating visible planets..." },
    { text: "fetching astronomical catalog..." },
    { text: "filtering visible objects..." },
    { text: "calculating object schedules..." },
    { text: "curating AI observation plan..." },
    { text: "enriching ephemerides with AI insights..." },
    { text: "generating visibility charts..." },
    { text: "creating PDF report..." },
    { text: "finalizing document..." },
  ];

  async function generatePlan() {
    loading = true;
    error = null;
    generatedPdfUrl = null;
    currentStep = 0;

    try {
      const response = await fetch(
        "http://localhost:8000/generate-plan-stream",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            lat,
            lon,
            date: new Date(date).toISOString(),
            telescope,
            language,
          }),
        },
      );

      if (!response.ok) {
        throw new Error("Failed to start plan generation");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No response body");
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = JSON.parse(line.slice(6));

            if (data.error) {
              throw new Error(data.error);
            }

            if (data.step !== undefined) {
              currentStep = data.step;
            }

            if (data.message === "complete" && data.report_id) {
              // Redirect to report page
              goto(`/report/${data.report_id}`);
            }
          }
        }
      }
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
      currentStep = 0;
    }
  }

  async function togglePastSessions() {
    if (showAbout) showAbout = false;
    showPastSessions = !showPastSessions;
  }

  async function toggleAbout() {
    if (showPastSessions) showPastSessions = false;
    showAbout = !showAbout;
  }
</script>

<div
  class="min-h-screen text-foreground flex flex-col items-start py-12 px-6 font-sans selection:bg-accent selection:text-accent-foreground max-w-3xl mx-auto relative z-10"
>
  <header class="mb-10 w-full flex items-center gap-4">
    <div class="shrink-0">
      <img
        src="/logo.png"
        alt="AstroBuddy logo"
        class="h-20 w-20 object-contain"
      />
    </div>
    <div class="space-y-1">
      <h1 class="text-4xl font-bold tracking-tight lowercase">astrobuddy</h1>
      <p class="text-muted-foreground lowercase">observation planning system</p>
    </div>
  </header>

  <main class="w-full space-y-8">
    <Tabs.Root value="session" class="w-full">
      <Tabs.List
        class="grid w-full grid-cols-2 border-b border-border rounded-none bg-transparent"
      >
        <Tabs.Trigger
          value="session"
          class="rounded-none px-4 py-2 text-sm font-medium lowercase data-[state=active]:border-b-2 data-[state=active]:border-foreground data-[state=active]:text-foreground text-muted-foreground data-[state=active]:bg-neutral-900/70"
        >
          session generator
        </Tabs.Trigger>
        <Tabs.Trigger
          value="catalog"
          class="rounded-none px-4 py-2 text-sm font-medium lowercase data-[state=active]:border-b-2 data-[state=active]:border-foreground data-[state=active]:text-foreground text-muted-foreground data-[state=active]:bg-neutral-900/60"
        >
          astronomical catalog management
        </Tabs.Trigger>
      </Tabs.List>

      <Tabs.Content value="session" class="mt-6">
        <Card class="border border-white/10 bg-neutral-900/60 shadow-lg">
          <CardContent class="p-6 space-y-10">
            {#if !showPastSessions && !showAbout}
              <!-- Original Generator Content -->
              <div transition:fade={{ duration: 300, easing: quintOut }}>
                <!-- Location Section -->
                <section class="space-y-4">
                  <div class="flex items-baseline justify-between">
                    <Label class="text-lg font-medium lowercase">Location</Label
                    >
                    <span class="text-xs text-muted-foreground font-mono">
                      {lat.toFixed(4)}, {lon.toFixed(4)}
                    </span>
                  </div>
                  <p class="text-sm text-muted-foreground lowercase max-w">
                    set the location as close as possible to your real observing
                    site. this is used for altitude, visibility windows and also
                    for the local weather forecast that feeds the observing
                    plan.
                  </p>
                  <div class="h-[30rem] w-full overflow-hidden">
                    <MapPicker bind:lat bind:lon />
                  </div>
                </section>

                <!-- Date & Equipment Section -->
                <section class="space-y-8 mt-10">
                  <div class="space-y-4">
                    <Label class="text-lg font-medium lowercase">Date</Label>
                    <p class="text-sm text-muted-foreground lowercase max-w">
                      choose the night you plan to observe. the date is used to
                      compute object positions, rise and set times and moon
                      phase, so accurate dates give more realistic time windows.
                    </p>
                    <DatePicker bind:date />
                  </div>

                  <div class="space-y-4">
                    <Label class="text-lg font-medium lowercase"
                      >Equipment</Label
                    >
                    <p class="text-sm text-muted-foreground lowercase max-w">
                      describe your telescope as precisely as you can (aperture,
                      focal length and type). this is used to estimate useful
                      magnifications, fields of view and recommendations
                      tailored to your setup.
                    </p>
                    <TelescopeInput on:change={handleTelescopeChange} />
                  </div>

                  <div class="space-y-4">
                    <Label class="text-lg font-medium lowercase">Language</Label
                    >
                    <p class="text-sm text-muted-foreground lowercase max-w">
                      select the language for AI-generated content in your
                      observation plan. all AI descriptions, tips and insights
                      will be written in your chosen language.
                    </p>
                    <ToggleGroup
                      bind:value={language}
                      type="single"
                      class="w-full"
                    >
                      <ToggleGroupItem value="english" class="flex-1">
                        <span class="mr-2">🇬🇧</span> English
                      </ToggleGroupItem>
                      <ToggleGroupItem value="spanish" class="flex-1">
                        <span class="mr-2">🇪🇸</span> Español
                      </ToggleGroupItem>
                    </ToggleGroup>
                  </div>
                </section>

                <!-- Action & Result Section -->
                <section class="pt-4 space-y-6 mt-10">
                  <div>
                    <Button
                      on:click={generatePlan}
                      disabled={loading}
                      class="w-full h-14 text-lg tracking-wide border border-green-400 text-green-400  hover:bg-green-400/50 uppercase"
                      variant="ghost"
                    >
                      {#if loading}
                        <span class="animate-pulse">generating...</span>
                      {:else}
                        generate plan
                      {/if}
                    </Button>

                    <Separator class="my-10" />

                    <div class="space-y-3">
                      <!-- Past Sessions Toggle Button -->
                      <button
                        on:click={togglePastSessions}
                        class="w-full flex items-center justify-between p-4 bg-gradient-to-r from-neutral-900/80 to-neutral-900/60 border border-white/10 hover:border-white/20 transition-all duration-300 group cursor-pointer"
                      >
                        <div class="flex items-center gap-3">
                          <div
                            class="flex items-center justify-center w-8 h-8 rounded-full bg-green-500/20 group-hover:bg-green-500/30 transition-colors"
                          >
                            <Clock class="w-4 h-4 text-green-400" />
                          </div>
                          <span
                            class="text-sm font-medium lowercase text-foreground"
                          >
                            view past session plans
                          </span>
                        </div>
                        <ChevronRight
                          class="w-5 h-5 text-muted-foreground group-hover:text-foreground group-hover:translate-x-1 transition-all duration-300"
                        />
                      </button>

                      <!-- About AstroBuddy Toggle Button -->
                      <button
                        on:click={toggleAbout}
                        class="w-full flex items-center justify-between p-4 bg-gradient-to-r from-neutral-900/80 to-neutral-900/60 border border-white/10 hover:border-white/20 transition-all duration-300 group cursor-pointer"
                      >
                        <div class="flex items-center gap-3">
                          <div
                            class="flex items-center justify-center w-8 h-8 rounded-full bg-green-500/20 group-hover:bg-green-500/30 transition-colors"
                          >
                            <Info class="w-4 h-4 text-green-400" />
                          </div>
                          <span
                            class="text-sm font-medium lowercase text-foreground"
                          >
                            about astrobuddy
                          </span>
                        </div>
                        <ChevronRight
                          class="w-5 h-5 text-muted-foreground group-hover:text-foreground group-hover:translate-x-1 transition-all duration-300"
                        />
                      </button>
                    </div>

                    {#if error}
                      <div
                        class="mt-4 p-4 text-destructive text-sm bg-destructive/10 border border-destructive/20 text-center"
                      >
                        error: {error}
                      </div>
                    {/if}
                  </div>

                  {#if generatedPdfUrl}
                    <div
                      class="animate-in fade-in slide-in-from-bottom-4 duration-500 pt-4 border-t border-border"
                    >
                      <Card
                        class="border border-white/10 bg-neutral-900/60 shadow-lg"
                      >
                        <CardHeader>
                          <div class="flex items-center justify-between">
                            <div>
                              <CardTitle class="text-xl lowercase"
                                >plan ready</CardTitle
                              >
                              <CardDescription class="lowercase"
                                >session prepared</CardDescription
                              >
                            </div>
                            <a
                              href={generatedPdfUrl}
                              download="observation_plan.pdf"
                              class="inline-flex items-center justify-center text-sm font-medium transition-colors hover:text-accent underline underline-offset-4 lowercase"
                            >
                              download pdf
                            </a>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div
                            class="aspect-[1/1.4] w-full border border-border bg-black/50 backdrop-blur-sm"
                          >
                            <iframe
                              src={generatedPdfUrl}
                              class="w-full h-full"
                              title="PDF Preview"
                            ></iframe>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  {/if}
                </section>
              </div>
            {:else if showPastSessions}
              <!-- Past Sessions List -->
              <div transition:fade={{ duration: 300, easing: quintOut }}>
                <PastSessionsView on:back={togglePastSessions} />
              </div>
            {:else if showAbout}
              <!-- About AstroBuddy -->
              <div transition:fade={{ duration: 300, easing: quintOut }}>
                <AboutView on:back={toggleAbout} />
              </div>
            {/if}
          </CardContent>
        </Card>
      </Tabs.Content>

      <Tabs.Content value="catalog" class="mt-6">
        <Card class="border border-white/10 bg-neutral-900/60 shadow-lg">
          <CardContent class="p-6">
            <CatalogView />
          </CardContent>
        </Card>
      </Tabs.Content>
    </Tabs.Root>
  </main>
</div>

<!-- Multi-step loader for PDF generation -->
<MultiStepLoader {loadingStates} {loading} {currentStep} />
