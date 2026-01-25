<script lang="ts">
  import Clock from "lucide-svelte/icons/clock";
  import ChevronRight from "lucide-svelte/icons/chevron-right";
  import CheckCircle2 from "lucide-svelte/icons/check-circle-2";
  import { onMount, createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher();

  let sessions: any[] = [];
  let loading = false;
  let error: string | null = null;

  async function loadSessions() {
    loading = true;
    error = null;
    try {
      const response = await fetch("http://localhost:8000/past-sessions");
      if (response.ok) {
        const data = await response.json();
        sessions = data.sessions || [];
      } else {
        error = "Failed to load sessions";
      }
    } catch (e) {
      console.error("Error loading past sessions:", e);
      error = "Error loading sessions";
    } finally {
      loading = false;
    }
  }

  function formatDate(timestamp: number) {
    return new Date(timestamp * 1000).toLocaleDateString("es", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function handleBack() {
    dispatch("back");
  }

  onMount(() => {
    loadSessions();
  });
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h2 class="text-2xl font-bold lowercase tracking-tight">
        past session plans
      </h2>
      <p class="text-sm text-muted-foreground lowercase mt-1">
        view and access your previous observation sessions
      </p>
    </div>
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

  {#if loading}
    <div class="flex items-center justify-center py-12">
      <div class="animate-pulse text-muted-foreground">loading sessions...</div>
    </div>
  {:else if error}
    <div
      class="mt-4 p-4 text-destructive text-sm bg-destructive/10 border border-destructive/20 text-center"
    >
      {error}
    </div>
  {:else if sessions.length === 0}
    <div class="text-center py-12 space-y-2">
      <Clock class="w-12 h-12 mx-auto text-muted-foreground opacity-50" />
      <p class="text-muted-foreground lowercase">no past sessions found</p>
      <p class="text-sm text-muted-foreground lowercase">
        generate your first observation plan to get started
      </p>
    </div>
  {:else}
    <div class="space-y-3">
      {#each sessions as session}
        <a
          href="/report/{session.id}"
          class="block p-5 bg-neutral-900/40 border border-white/10 hover:border-white/20 hover:bg-neutral-900/60 transition-all duration-200 group"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 space-y-2">
              <div class="flex items-center gap-2">
                <Clock class="w-4 h-4 text-blue-400" />
                <span class="text-sm font-mono text-muted-foreground">
                  {formatDate(session.created_at)}
                </span>
              </div>
              <div class="space-y-1">
                <p class="text-sm text-foreground lowercase">
                  <span class="font-medium">location:</span>
                  {session.location?.lat?.toFixed(2)}, {session.location?.lon?.toFixed(
                    2,
                  )}
                </p>
                <p class="text-sm text-muted-foreground lowercase">
                  <span class="font-medium">telescope:</span>
                  {session.telescope}
                </p>
                <p class="text-sm text-muted-foreground lowercase">
                  <span class="font-medium">objects:</span>
                  {session.objects_count}
                </p>
              </div>
            </div>
            <ChevronRight
              class="w-5 h-5 text-muted-foreground group-hover:text-foreground group-hover:translate-x-1 transition-all duration-200 shrink-0 mt-1"
            />
          </div>
        </a>
      {/each}
    </div>
  {/if}
</div>
