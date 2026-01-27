<script lang="ts">
  import { onMount } from "svelte";
  import { toast } from "svelte-sonner";
  import { API_URL } from "$lib/config";
  import { Input } from "$lib/components/ui/input";
  import { Button } from "$lib/components/ui/button";
  import { Card, CardContent } from "$lib/components/ui/card";
  import * as HoverCard from "$lib/components/ui/hover-card";
  import * as AlertDialog from "$lib/components/ui/alert-dialog";
  import AddObjectDialog from "./AddObjectDialog.svelte";
  import ChevronLeft from "lucide-svelte/icons/chevron-left";
  import ChevronRight from "lucide-svelte/icons/chevron-right";
  import Trash2 from "lucide-svelte/icons/trash-2";

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
  let showAddDialog = false;
  let deletingId: string | null = null;
  let showDeleteDialog = false;
  let objectToDelete: { id: string; name: string } | null = null;
  let openHoverCardId: string | null = null;

  // Pagination state
  const ITEMS_PER_PAGE = 20;
  let currentPage = 1;
  let totalPages = 1;
  let paginatedObjects: CelestialObject[] = [];

  const DEFAULT_IMAGE = "/default-celestial.svg";

  onMount(() => {
    loadObjects();
  });

  async function loadObjects() {
    loading = true;
    error = null;
    try {
      const response = await fetch(`${API_URL}/catalog/objects`);
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
        `${API_URL}/catalog/objects?search=${encodeURIComponent(searchQuery)}`,
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

  function handleObjectCreated() {
    // Reload the catalog after creating a new object
    loadObjects();
  }

  function promptDeleteObject(id: string, name: string) {
    objectToDelete = { id, name };
    openHoverCardId = null; // Close the hover card
    showDeleteDialog = true;
  }

  async function confirmDelete() {
    if (!objectToDelete) return;

    deletingId = objectToDelete.id;
    try {
      const response = await fetch(
        `${API_URL}/catalog/objects/${encodeURIComponent(deletingId)}`,
        {
          method: "DELETE",
        },
      );

      if (!response.ok) {
        throw new Error("Failed to delete object");
      }

      toast.success(`${name} deleted successfully`, {
        duration: 3000,
      });

      // Reload objects
      await loadObjects();
    } catch (e: any) {
      toast.error("Failed to delete object", {
        description: e.message,
        duration: 4000,
      });
    } finally {
      deletingId = null;
      showDeleteDialog = false;
      objectToDelete = null;
    }
  }

  // Update pagination when filtered objects change
  $: {
    totalPages = Math.ceil(filteredObjects.length / ITEMS_PER_PAGE);
    if (currentPage > totalPages && totalPages > 0) {
      currentPage = totalPages;
    }
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    paginatedObjects = filteredObjects.slice(startIndex, endIndex);
  }

  function nextPage() {
    if (currentPage < totalPages) {
      currentPage++;
    }
  }

  function prevPage() {
    if (currentPage > 1) {
      currentPage--;
    }
  }
</script>

<div class="space-y-6">
  <!-- Overlay when hover card is open -->
  {#if openHoverCardId !== null}
    <div
      class="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm pointer-events-none"
    />
  {/if}

  <div class="flex items-start justify-between gap-4">
    <div class="space-y-2">
      <h2 class="text-2xl font-bold tracking-tight">astronomical catalog</h2>
      <p class="text-muted-foreground">
        explore and manage your collection of celestial objects
      </p>
    </div>
    <Button
      on:click={() => (showAddDialog = true)}
      class="border-green-500 hover:bg-green-500 text-white shrink-0"
    >
      + add object
    </Button>
  </div>

  <!-- Search Bar -->
  <div class="w-full max-w-2xl">
    <Input
      type="text"
      placeholder="search by name, id, type, constellation or catalog..."
      bind:value={searchQuery}
      class="h-12 text-base bg-neutral-900/60 border-white/10"
    />
  </div>

  <!-- Loading State -->
  {#if loading && filteredObjects.length === 0}
    <div class="text-center py-12">
      <p class="text-muted-foreground animate-pulse">loading...</p>
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
        <p class="text-muted-foreground">no objects found</p>
      </div>
    {:else}
      <!-- Pagination Controls -->
      <div class="flex items-center justify-between">
        <p class="text-sm text-muted-foreground">
          showing {(currentPage - 1) * ITEMS_PER_PAGE + 1}-{Math.min(
            currentPage * ITEMS_PER_PAGE,
            filteredObjects.length,
          )} of {filteredObjects.length} objects
        </p>
        <div class="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            on:click={prevPage}
            disabled={currentPage === 1}
          >
            <ChevronLeft class="w-4 h-4" />
          </Button>
          <span class="text-sm font-mono">
            {currentPage} / {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            on:click={nextPage}
            disabled={currentPage === totalPages}
          >
            <ChevronRight class="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div
        class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4"
      >
        {#each paginatedObjects as object (object.id)}
          <HoverCard.Root
            openDelay={200}
            open={openHoverCardId === object.id}
            onOpenChange={(isOpen) => {
              openHoverCardId = isOpen ? object.id : null;
            }}
          >
            <HoverCard.Trigger>
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
                        class="absolute top-2 right-2 px-2 py-1 bg-black/70 backdrop-blur-sm text-xs font-mono text-white/80"
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
                    <p class="text-sm font-medium truncate">
                      {object.name}
                    </p>
                    <p class="text-xs text-muted-foreground truncate">
                      {object.type}
                      {#if object.constellation}
                        · {object.constellation}
                      {/if}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </HoverCard.Trigger>
            <HoverCard.Content
              class="w-80 bg-neutral-900/95 backdrop-blur-md border-white/20 !rounded-none"
            >
              <div class="space-y-3">
                <!-- Header with name and delete button -->
                <div class="flex items-start justify-between gap-2">
                  <div class="flex-1 min-w-0">
                    <h3 class="text-xl font-bold truncate">{object.name}</h3>
                    <p
                      class="text-xs font-mono text-muted-foreground uppercase"
                    >
                      {object.id}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    on:click={() => promptDeleteObject(object.id, object.name)}
                    disabled={deletingId === object.id}
                    class="shrink-0 h-8 w-8 p-0 hover:bg-red-500/20 text-red-500"
                  >
                    {#if deletingId === object.id}
                      <span class="animate-spin">⏳</span>
                    {:else}
                      <Trash2 class="w-4 h-4" />
                    {/if}
                  </Button>
                </div>

                <!-- Details Grid -->
                <div class="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <p class="text-muted-foreground">type</p>
                    <p class="font-medium">{object.type}</p>
                  </div>
                  {#if object.constellation}
                    <div>
                      <p class="text-muted-foreground">constellation</p>
                      <p class="font-medium">{object.constellation}</p>
                    </div>
                  {/if}
                  <div>
                    <p class="text-muted-foreground">magnitude</p>
                    <p class="font-medium font-mono">
                      {object.mag?.toFixed(1) ?? "N/A"}
                    </p>
                  </div>
                  {#if object.size}
                    <div>
                      <p class="text-muted-foreground">size</p>
                      <p class="font-medium font-mono">{object.size}'</p>
                    </div>
                  {/if}
                  <div>
                    <p class="text-muted-foreground">ra</p>
                    <p class="font-medium font-mono">
                      {object.ra.toFixed(4)}°
                    </p>
                  </div>
                  <div>
                    <p class="text-muted-foreground">dec</p>
                    <p class="font-medium font-mono">
                      {object.dec.toFixed(4)}°
                    </p>
                  </div>
                  {#if object.catalog}
                    <div class="pt-2 border-t border-white/10">
                      <p class="text-muted-foreground">catalog</p>
                      <p class="font-medium">{object.catalog}</p>
                    </div>
                  {/if}
                  {#if object.ngc}
                    <div class="pt-2 border-t border-white/10">
                      <p class="text-muted-foreground">ngc</p>
                      <p class="font-medium font-mono">{object.ngc}</p>
                    </div>
                  {/if}
                </div>

                {#if object.description}
                  <div class="pt-2 border-t border-white/10">
                    <p class="text-xs text-muted-foreground">description</p>
                    <p class="text-xs mt-1">{object.description}</p>
                  </div>
                {/if}
              </div>
            </HoverCard.Content>
          </HoverCard.Root>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<!-- Add Object Dialog -->
<AddObjectDialog
  bind:open={showAddDialog}
  on:objectCreated={handleObjectCreated}
/>

<!-- Delete Confirmation Dialog -->
<AlertDialog.Root bind:open={showDeleteDialog}>
  <AlertDialog.Content>
    <AlertDialog.Header>
      <AlertDialog.Title>confirm deletion</AlertDialog.Title>
      <AlertDialog.Description>
        are you sure you want to delete <span class="font-semibold"
          >{objectToDelete?.name}</span
        >? this action cannot be undone.
      </AlertDialog.Description>
    </AlertDialog.Header>
    <AlertDialog.Footer>
      <AlertDialog.Cancel>cancel</AlertDialog.Cancel>
      <AlertDialog.Action
        on:click={confirmDelete}
        class="bg-red-600 hover:bg-red-700 text-white"
      >
        {deletingId ? "deleting..." : "delete"}
      </AlertDialog.Action>
    </AlertDialog.Footer>
  </AlertDialog.Content>
</AlertDialog.Root>
