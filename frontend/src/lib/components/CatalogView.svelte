<script lang="ts">
  import { onMount } from "svelte";
  import { Input } from "$lib/components/ui/input";
  import { Card, CardContent } from "$lib/components/ui/card";

  interface CelestialObject {
    id: string;
    name: string;
    ngc?: string;
    ra: number;
    dec: number;
    mag: number;
    size?: string;
    type: string;
    constellation?: string;
    description?: string;
    catalog?: string;
    image_url?: string;
    created_at?: string;
  }

  let objects: CelestialObject[] = [];
  let filteredObjects: CelestialObject[] = [];
  let searchQuery = "";
  let loading = false;
  let error: string | null = null;

  const DEFAULT_IMAGE = "/default-celestial.svg";

  onMount(() => {
    loadObjects();
  });

  async function loadObjects() {
    loading = true;
    error = null;
    try {
      const response = await fetch("http://localhost:8000/catalog/objects");
      if (!response.ok) {
        throw new Error("Failed to load catalog");
      }
      const data = await response.json();
      objects = data.objects || [];
      filteredObjects = objects;
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function handleSearch() {
    if (!searchQuery.trim()) {
      filteredObjects = objects;
      return;
    }

    loading = true;
    error = null;
    try {
      const response = await fetch(
        `http://localhost:8000/catalog/objects?search=${encodeURIComponent(searchQuery)}`,
      );
      if (!response.ok) {
        throw new Error("Search failed");
      }
      const data = await response.json();
      filteredObjects = data.objects || [];
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function handleImageError(event: Event) {
    const img = event.target as HTMLImageElement;
    img.src = DEFAULT_IMAGE;
  }

  // Debounce search - específicamente escuchando a searchQuery
  let searchTimeout: ReturnType<typeof setTimeout>;
  $: if (searchQuery !== undefined) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      handleSearch();
    }, 300);
  }
</script>

<div class="space-y-6">
  <div class="space-y-2">
    <h2 class="text-2xl font-bold tracking-tight lowercase">
      catálogo astronómico
    </h2>
    <p class="text-muted-foreground lowercase">
      explora y gestiona tu colección de objetos celestes
    </p>
  </div>

  <!-- Search Bar -->
  <div class="w-full max-w-2xl">
    <Input
      type="text"
      placeholder="buscar por nombre, id, tipo, constelación o catálogo..."
      bind:value={searchQuery}
      class="h-12 text-base lowercase bg-neutral-900/60 border-white/10"
    />
  </div>

  <!-- Loading State -->
  {#if loading && filteredObjects.length === 0}
    <div class="text-center py-12">
      <p class="text-muted-foreground animate-pulse lowercase">cargando...</p>
    </div>
  {/if}

  <!-- Error State -->
  {#if error}
    <div
      class="p-4 text-destructive text-sm bg-destructive/10 border border-destructive/20"
    >
      error: {error}
    </div>
  {/if}

  <!-- Objects Grid -->
  {#if !loading || filteredObjects.length > 0}
    {#if filteredObjects.length === 0}
      <div class="text-center py-12">
        <p class="text-muted-foreground lowercase">no se encontraron objetos</p>
      </div>
    {:else}
      <div
        class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4"
      >
        {#each filteredObjects as object (object.id)}
          <Card
            class="border border-white/10 bg-neutral-900/60 hover:bg-neutral-900/80 transition-colors cursor-pointer overflow-hidden group"
          >
            <CardContent class="p-0">
              <!-- Image Container -->
              <div
                class="aspect-square w-full bg-black/50 overflow-hidden relative"
              >
                <img
                  src={object.image_url || DEFAULT_IMAGE}
                  alt={object.name}
                  on:error={handleImageError}
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                {#if object.catalog}
                  <div
                    class="absolute top-2 right-2 px-2 py-1 bg-black/70 backdrop-blur-sm text-xs font-mono text-white/80 rounded"
                  >
                    {object.catalog}
                  </div>
                {/if}
              </div>

              <!-- Info -->
              <div class="p-3 space-y-1">
                <p
                  class="text-xs font-mono text-muted-foreground truncate uppercase"
                >
                  {object.id}
                </p>
                <p class="text-sm font-medium truncate lowercase">
                  {object.name}
                </p>
                <p class="text-xs text-muted-foreground truncate lowercase">
                  {object.type}
                  {#if object.constellation}
                    · {object.constellation}
                  {/if}
                </p>
              </div>
            </CardContent>
          </Card>
        {/each}
      </div>
    {/if}
  {/if}
</div>
