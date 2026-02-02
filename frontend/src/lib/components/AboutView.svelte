<script lang="ts">
  import ChevronRight from "lucide-svelte/icons/chevron-right";
  import CheckCircle2 from "lucide-svelte/icons/check-circle-2";
  import Sparkles from "lucide-svelte/icons/sparkles";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  function handleBack() {
    dispatch("back");
  }
</script>

<div class="space-y-8">
  <div class="space-y-2">
    <h2 class="text-2xl font-bold lowercase tracking-tight">
      about astrobuddy
    </h2>
    <p class="text-sm text-muted-foreground lowercase">
      your intelligent observation planning companion
    </p>
  </div>

  <!-- Back Button -->
  <button
    on:click={handleBack}
    class="w-full flex items-center justify-between p-4 bg-gradient-to-r from-neutral-900/80 to-neutral-900/60 border border-white/10 hover:border-white/20 transition-all duration-300 group cursor-pointer"
  >
    <div class="flex items-center gap-3">
      <div
        class="flex items-center justify-center w-8 h-8 rounded-full bg-green-500/20 group-hover:bg-green-500/30 transition-colors"
      >
        <CheckCircle2 class="w-4 h-4 text-green-400" />
      </div>
      <span class="text-sm font-medium lowercase text-foreground">
        back to session generator
      </span>
    </div>
    <ChevronRight
      class="w-5 h-5 text-muted-foreground group-hover:text-foreground group-hover:-translate-x-1 transition-all duration-300"
      style="transform: rotate(180deg);"
    />
  </button>

  <!-- What is AstroBuddy -->
  <section class="space-y-4">
    <div class="flex items-center gap-2">
      <Sparkles class="w-5 h-5 text-green-400" />
      <h3 class="text-xl font-semibold lowercase">what is astrobuddy?</h3>
    </div>
    <div class="space-y-3 text-sm text-muted-foreground leading-relaxed">
      <p>
        astrobuddy is an intelligent observation planning system that combines
        astronomical computation, real-time weather data, and artificial
        intelligence to create personalized observation plans for amateur
        astronomers.
      </p>
      <p>
        instead of spending hours manually researching what's visible, when to
        observe it, and what conditions to expect, astrobuddy does all the heavy
        lifting for you, delivering a comprehensive PDF report tailored to your
        location, equipment, and chosen observation date.
      </p>
    </div>
  </section>

  <!-- How it Works -->
  <section class="space-y-4">
    <div class="flex items-center gap-2">
      <Sparkles class="w-5 h-5 text-green-400" />
      <h3 class="text-xl font-semibold lowercase">how does it work?</h3>
    </div>
    <div class="space-y-4">
      <div class="space-y-2">
        <div
          class="flex items-start gap-3 p-4 bg-neutral-900/40 border border-white/10"
        >
          <div
            class="flex items-center justify-center w-8 h-8 rounded-full bg-green-500/20 shrink-0"
          >
            <span class="text-sm font-mono text-green-400">1</span>
          </div>
          <div class="flex-1 space-y-1">
            <h4 class="font-medium text-foreground lowercase">
              astronomical calculations
            </h4>
            <p class="text-sm text-muted-foreground">
              using <span class="text-green-400 font-mono">skyfield</span> and precise
              ephemerides, astrobuddy calculates your local astronomical darkness
              window (when the sun is more than 18° below the horizon), sunrise/sunset
              times, moon phase and illumination, and planetary positions for your
              exact location and date.
            </p>
          </div>
        </div>

        <div
          class="flex items-start gap-3 p-4 bg-neutral-900/40 border border-white/10"
        >
          <div
            class="flex items-center justify-center w-8 h-8 rounded-full bg-green-500/20 shrink-0"
          >
            <span class="text-sm font-mono text-green-400">2</span>
          </div>
          <div class="flex-1 space-y-1">
            <h4 class="font-medium text-foreground lowercase">
              weather forecast
            </h4>
            <p class="text-sm text-muted-foreground">
              astrobuddy fetches hourly weather forecasts specifically for your
              observation window, including cloud coverage, temperature,
              humidity, and wind speed. this data is used to provide
              hour-by-hour observing conditions and recommendations.
            </p>
          </div>
        </div>

        <div
          class="flex items-start gap-3 p-4 bg-neutral-900/40 border border-white/10"
        >
          <div
            class="flex items-center justify-center w-8 h-8 rounded-full bg-green-500/20 shrink-0"
          >
            <span class="text-sm font-mono text-green-400">3</span>
          </div>
          <div class="flex-1 space-y-1">
            <h4 class="font-medium text-foreground lowercase">
              catalog querying
            </h4>
            <p class="text-sm text-muted-foreground">
              the system queries professional astronomical databases including
              <span class="text-green-400 font-mono">SIMBAD</span>
              (operated by CDS, Strasbourg) and
              <span class="text-green-400 font-mono">VizieR</span>
              catalogs to access data on deep-sky objects. it uses
              <span class="text-green-400 font-mono">astroquery</span>
              to interface with these services, retrieving accurate coordinates,
              magnitudes, sizes, and object types.
            </p>
          </div>
        </div>

        <div
          class="flex items-start gap-3 p-4 bg-neutral-900/40 border border-white/10"
        >
          <div
            class="flex items-center justify-center w-8 h-8 rounded-full bg-green-500/20 shrink-0"
          >
            <span class="text-sm font-mono text-green-400">4</span>
          </div>
          <div class="flex-1 space-y-1">
            <h4 class="font-medium text-foreground lowercase">
              visibility filtering
            </h4>
            <p class="text-sm text-muted-foreground">
              objects from the catalog are filtered based on your location and
              observation window. astrobuddy calculates altitude above the
              horizon throughout the night, filtering out objects that never
              rise high enough for good observation (typically &gt;30°
              altitude).
            </p>
          </div>
        </div>

        <div
          class="flex items-start gap-3 p-4 bg-neutral-900/40 border border-white/10"
        >
          <div
            class="flex items-center justify-center w-8 h-8 rounded-full bg-green-500/20 shrink-0"
          >
            <span class="text-sm font-mono text-green-400">5</span>
          </div>
          <div class="flex-1 space-y-1">
            <h4 class="font-medium text-foreground lowercase">
              schedule computation
            </h4>
            <p class="text-sm text-muted-foreground">
              for each visible object, the system calculates rise time, set
              time, transit time (when it's highest in the sky), and best
              observation window. this ensures you know exactly when to observe
              each target for optimal viewing.
            </p>
          </div>
        </div>

        <div
          class="flex items-start gap-3 p-4 bg-neutral-900/40 border border-white/10"
        >
          <div
            class="flex items-center justify-center w-8 h-8 rounded-full bg-green-500/20 shrink-0"
          >
            <span class="text-sm font-mono text-green-400">6</span>
          </div>
          <div class="flex-1 space-y-1">
            <h4 class="font-medium text-foreground lowercase">
              AI curation & insights
            </h4>
            <p class="text-sm text-muted-foreground">
              using
              <span class="text-green-400 font-mono">ChatGPT (GPT-4o)</span>,
              astrobuddy analyzes all the technical data (object schedules,
              weather conditions, your telescope capabilities) and generates
              intelligent recommendations. the AI prioritizes objects based on
              observability, weather windows, and your equipment, and provides
              detailed observing tips, what to look for, and optimal viewing
              strategies for each target.
            </p>
          </div>
        </div>

        <div
          class="flex items-start gap-3 p-4 bg-neutral-900/40 border border-white/10"
        >
          <div
            class="flex items-center justify-center w-8 h-8 rounded-full bg-green-500/20 shrink-0"
          >
            <span class="text-sm font-mono text-green-400">7</span>
          </div>
          <div class="flex-1 space-y-1">
            <h4 class="font-medium text-foreground lowercase">
              visualization & reporting
            </h4>
            <p class="text-sm text-muted-foreground">
              finally, astrobuddy compiles detailed visibility metrics for each
              object, integrates weather conditions, and generates a
              comprehensive PDF report. the report includes moon phase images
              from
              <span class="text-green-400 font-mono">NASA SVS</span>, technical
              ephemerides, AI-generated insights, and a complete observation
              schedule.
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Technologies -->
  <section class="space-y-4">
    <div class="flex items-center gap-2">
      <Sparkles class="w-5 h-5 text-green-400" />
      <h3 class="text-xl font-semibold lowercase">astronomical data sources</h3>
    </div>
    <div class="space-y-3">
      <div class="p-4 bg-neutral-900/40 border border-white/10 space-y-2">
        <h4 class="font-medium text-green-400 font-mono">skyfield</h4>
        <p class="text-sm text-muted-foreground">
          elegant python astronomy library. used for high-precision ephemeris
          calculations, rise/set times, moon phases, and coordinate
          transformations.
        </p>
      </div>

      <div class="p-4 bg-neutral-900/40 border border-white/10 space-y-2">
        <h4 class="font-medium text-green-400 font-mono">astropy</h4>
        <p class="text-sm text-muted-foreground">
          community-developed core python library for astronomy. used for
          catalog querying and additional coordinate utilities.
        </p>
      </div>

      <div class="p-4 bg-neutral-900/40 border border-white/10 space-y-2">
        <h4 class="font-medium text-green-400 font-mono">SIMBAD</h4>
        <p class="text-sm text-muted-foreground">
          astronomical database operated by CDS (Centre de Données astronomiques
          de Strasbourg). provides comprehensive data on astronomical objects
          outside our solar system.
        </p>
      </div>

      <div class="p-4 bg-neutral-900/40 border border-white/10 space-y-2">
        <h4 class="font-medium text-green-400 font-mono">VizieR</h4>
        <p class="text-sm text-muted-foreground">
          astronomical catalog service providing access to published catalogs
          including Messier, NGC/IC, and thousands of others.
        </p>
      </div>

      <div class="p-4 bg-neutral-900/40 border border-white/10 space-y-2">
        <h4 class="font-medium text-green-400 font-mono">astroquery</h4>
        <p class="text-sm text-muted-foreground">
          python interface to astronomical databases and services. enables
          programmatic access to SIMBAD, VizieR, and other professional
          astronomical data sources.
        </p>
      </div>

      <div class="p-4 bg-neutral-900/40 border border-white/10 space-y-2">
        <h4 class="font-medium text-green-400 font-mono">NASA SVS</h4>
        <p class="text-sm text-muted-foreground">
          NASA Scientific Visualization Studio provides accurate moon phase
          imagery used in observation reports.
        </p>
      </div>

      <div class="p-4 bg-neutral-900/40 border border-white/10 space-y-2">
        <h4 class="font-medium text-green-400 font-mono">OpenAI GPT-4o</h4>
        <p class="text-sm text-muted-foreground">
          advanced language model that analyzes astronomical and meteorological
          data to generate intelligent, context-aware observation
          recommendations and detailed observing guidance.
        </p>
      </div>

      <div class="p-4 bg-neutral-900/40 border border-white/10 space-y-2">
        <h4 class="font-medium text-green-400 font-mono">Open-Meteo API</h4>
        <p class="text-sm text-muted-foreground">
          open-source weather API providing hourly forecasts for any location
          worldwide, used for observing condition predictions.
        </p>
      </div>
    </div>
  </section>

  <!-- Footer note -->
  <div class="pt-4 border-t border-white/10">
    <p class="text-xs text-muted-foreground text-center lowercase">
      astrobuddy combines professional-grade astronomical tools with modern AI
      to make observation planning accessible and efficient for everyone.
    </p>
    <br />
    <p class="text-sm text-center lowercase">
      by tomas vergara / <a
        class="underline"
        href="https://github.com/TOMIVERGARA">GitHub</a
      > - 2026
    </p>
  </div>
</div>
