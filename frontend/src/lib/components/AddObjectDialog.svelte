<script lang="ts">
  import { createEventDispatcher, tick } from "svelte";
  import { slide, fly } from "svelte/transition";
  import { toast } from "svelte-sonner";
  import * as Dialog from "$lib/components/ui/dialog";
  import { Button } from "$lib/components/ui/button";
  import { Input } from "$lib/components/ui/input";
  import { Label } from "$lib/components/ui/label";
  import * as Command from "$lib/components/ui/command";
  import * as Popover from "$lib/components/ui/popover";
  import { cn } from "$lib/utils";
  import CheckIcon from "lucide-svelte/icons/check";
  import ChevronsUpDownIcon from "lucide-svelte/icons/chevrons-up-down";
  import Search from "lucide-svelte/icons/search";
  import Loader from "lucide-svelte/icons/loader";
  import Sparkles from "lucide-svelte/icons/sparkles";
  import ImageIcon from "lucide-svelte/icons/image";

  export let open = false;

  const dispatch = createEventDispatcher();

  interface ObjectData {
    id: string;
    name: string;
    ngc?: string;
    ra: number | null;
    dec: number | null;
    mag: number | null;
    size?: string;
    type: string;
    constellation?: string;
    description?: string;
    catalog?: string;
    image_url?: string;
  }

  let searchId = "";
  let objectData: ObjectData = {
    id: "",
    name: "",
    ra: null,
    dec: null,
    mag: null,
    type: "",
  };

  let images: Array<{ url: string; title: string; description: string }> = [];
  let currentImageIndex = 0;
  let loading = false;
  let lookupLoading = false;
  let imagesLoading = false;
  let error: string | null = null;
  let searchPerformed = false;
  let objectNotFound = false;

  const DEFAULT_IMAGE = "/default-celestial.svg";

  // Catalog dropdown state
  const catalogs = [
    { value: "Messier", label: "Messier" },
    { value: "NGC", label: "NGC" },
    { value: "IC", label: "IC (Index Catalogue)" },
    { value: "Caldwell", label: "Caldwell" },
    { value: "Collinder", label: "Collinder" },
    { value: "Melotte", label: "Melotte" },
    { value: "Barnard", label: "Barnard" },
    { value: "Sharpless", label: "Sharpless" },
    { value: "Abell", label: "Abell" },
  ];

  let catalogOpen = false;

  async function lookupObject() {
    if (!searchId.trim()) return;

    lookupLoading = true;
    error = null;
    objectNotFound = false;

    try {
      const response = await fetch(
        `http://localhost:8000/catalog/lookup/${encodeURIComponent(searchId)}`,
      );

      if (!response.ok) {
        // Object not found, allow manual completion
        objectNotFound = true;
        objectData = {
          id: searchId.toUpperCase(),
          name: "",
          ra: null,
          dec: null,
          mag: null,
          size: "",
          type: "",
          constellation: "",
          description: "",
          catalog: "",
          image_url: DEFAULT_IMAGE,
        };
        images = [];
        searchPerformed = true;
        return;
      }

      const data = await response.json();
      objectNotFound = false;

      // Populate form with fetched data
      objectData = {
        id: data.id || searchId.toUpperCase(),
        name: data.name || "",
        ra: data.ra,
        dec: data.dec,
        mag: data.mag,
        size: data.size,
        type: data.type || "",
        constellation: data.constellation || "",
        description: "",
        catalog: "",
        image_url: "",
      };

      // Also fetch images
      await fetchImages();
      searchPerformed = true;
    } catch (e: any) {
      error = e.message;
    } finally {
      lookupLoading = false;
    }
  }

  async function fetchImages() {
    if (!searchId.trim()) return;

    imagesLoading = true;

    try {
      const response = await fetch(
        `http://localhost:8000/catalog/images/${encodeURIComponent(searchId)}`,
      );

      if (!response.ok) {
        console.warn("Failed to fetch images");
        images = [];
        return;
      }

      const data = await response.json();
      images = data.images || [];
      currentImageIndex = 0;

      if (images.length > 0) {
        objectData.image_url = images[0].url;
      } else {
        // Use default image if no images found
        objectData.image_url = DEFAULT_IMAGE;
      }
    } catch (e) {
      console.warn("Error fetching images:", e);
      images = [];
    } finally {
      imagesLoading = false;
    }
  }

  function nextImage() {
    if (images.length === 0) return;
    currentImageIndex = (currentImageIndex + 1) % images.length;
    objectData.image_url = images[currentImageIndex].url;
  }

  function prevImage() {
    if (images.length === 0) return;
    currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
    objectData.image_url = images[currentImageIndex].url;
  }

  async function handleSubmit() {
    loading = true;
    error = null;

    try {
      // Validate required fields
      if (
        !objectData.id ||
        !objectData.name ||
        objectData.ra === null ||
        objectData.dec === null ||
        objectData.mag === null ||
        !objectData.type
      ) {
        throw new Error("Please fill in all required fields");
      }

      const response = await fetch("http://localhost:8000/catalog/objects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...objectData,
          created_at: new Date().toISOString(),
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Failed to create object");
      }

      const newObject = await response.json();
      dispatch("objectCreated", newObject);

      // Show success notification
      toast.success(`${objectData.name} added successfully`, {
        description: `${objectData.type} • ${objectData.constellation || "unknown constellation"}`,
        duration: 4000,
      });

      // Reset form
      resetForm();
      open = false;
    } catch (e: any) {
      error = e.message;

      // Show error notification
      toast.error("failed to add object", {
        description: e.message,
        duration: 5000,
      });
    } finally {
      loading = false;
    }
  }

  function resetForm() {
    searchId = "";
    objectData = {
      id: "",
      name: "",
      ra: null,
      dec: null,
      mag: null,
      type: "",
    };
    images = [];
    currentImageIndex = 0;
    error = null;
    searchPerformed = false;
    objectNotFound = false;
  }

  function handleOpenChange(newOpen: boolean) {
    open = newOpen;
    if (!newOpen) {
      resetForm();
    }
  }

  function closeAndFocusCatalogTrigger() {
    catalogOpen = false;
  }

  $: selectedCatalog = catalogs.find(
    (c) => c.value === objectData.catalog,
  )?.label;
</script>

<Dialog.Root {open} onOpenChange={handleOpenChange}>
  <Dialog.Content
    class="max-w-4xl max-h-[90vh] transition-all duration-500 ease-in-out flex flex-col"
  >
    <Dialog.Header>
      <Dialog.Title>add new object</Dialog.Title>
      <Dialog.Description>
        search for an object by its identifier (e.g., M31, NGC224) to autofill
        information
      </Dialog.Description>
    </Dialog.Header>

    <div class="space-y-6 py-4 overflow-y-auto flex-1">
      <!-- Search Bar - Full Width -->
      <div class="flex gap-2">
        <Input
          bind:value={searchId}
          placeholder="M31, NGC224, IC1101..."
          on:keydown={(e) => e.key === "Enter" && lookupObject()}
        />
        <Button
          on:click={lookupObject}
          disabled={lookupLoading || !searchId.trim()}
          variant="outline"
          size="icon"
          class="shrink-0"
        >
          {#if lookupLoading}
            <span class="animate-spin"><Loader class="w-4" /></span>
          {:else}
            <Search class="w-4" />
          {/if}
        </Button>
      </div>

      {#if objectNotFound}
        <div
          class="p-3 text-yellow-500 text-sm bg-yellow-500/10 border border-yellow-500/20 flex items-center gap-2"
          transition:slide={{ duration: 200 }}
        >
          <Sparkles class="w-4 h-4" />
          <span
            >object not found in database - you can complete the form manually</span
          >
        </div>
      {:else if error}
        <div
          class="p-3 text-destructive text-sm bg-destructive/10 border border-destructive/20"
          transition:slide={{ duration: 200 }}
        >
          {error}
        </div>
      {/if}

      {#if searchPerformed}
        <!-- Two Column Layout: Image Left, Form Right -->
        <div
          class="grid grid-cols-1 md:grid-cols-[1fr_2fr] gap-4"
          transition:fly={{ y: 20, duration: 500 }}
        >
          <!-- Left Column: Image Preview -->
          <div class="space-y-2">
            {#if images.length > 0}
              <div class="space-y-1.5">
                <div
                  class="relative aspect-square max-w-64 mx-auto mt-10 bg-black/50 overflow-hidden border border-white/10"
                >
                  <img
                    src={images[currentImageIndex].url}
                    alt={images[currentImageIndex].title}
                    class="w-full h-full object-cover"
                  />
                </div>

                <!-- Image Navigation Buttons Below Image -->
                {#if images.length > 1}
                  <div class="flex items-center justify-center gap-2">
                    <Button on:click={prevImage} size="sm" variant="outline">
                      ←
                    </Button>
                    <span class="text-sm text-muted-foreground">
                      {currentImageIndex + 1} / {images.length}
                    </span>
                    <Button on:click={nextImage} size="sm" variant="outline">
                      →
                    </Button>
                  </div>
                {/if}

                <!-- Image Description -->
                {#if images[currentImageIndex].title || images[currentImageIndex].description}
                  <div class="text-xs text-muted-foreground space-y-1">
                    {#if images[currentImageIndex].title}
                      <p class="font-medium">
                        {images[currentImageIndex].title}
                      </p>
                    {/if}
                    {#if images[currentImageIndex].description}
                      <p>{images[currentImageIndex].description}</p>
                    {/if}
                  </div>
                {/if}
              </div>
            {:else if imagesLoading}
              <div
                class="aspect-square max-w-64 mx-auto mt-10 bg-black/50 border border-white/10 flex items-center justify-center"
              >
                <p class="text-sm text-muted-foreground animate-pulse">
                  searching for images...
                </p>
              </div>
            {:else}
              <div
                class="relative aspect-square max-w-64 mx-auto mt-10 bg-black/50 border border-white/10 overflow-hidden"
              >
                <img
                  src={DEFAULT_IMAGE}
                  alt="Default space image"
                  class="w-full h-full object-cover opacity-50"
                />
                <div
                  class="absolute inset-0 flex items-center justify-center bg-black/30"
                >
                  <div class="text-center space-y-2">
                    <ImageIcon class="w-10 h-10 mx-auto opacity-50" />
                  </div>
                </div>
              </div>
            {/if}
          </div>

          <!-- Right Column: Form Fields -->
          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1.5">
              <Label>id *</Label>
              <Input bind:value={objectData.id} required />
            </div>

            <div class="space-y-1.5">
              <Label>name *</Label>
              <Input bind:value={objectData.name} required />
            </div>

            <div class="space-y-1.5">
              <Label>ra (degrees) *</Label>
              <Input
                type="number"
                step="0.0001"
                bind:value={objectData.ra}
                required
              />
            </div>

            <div class="space-y-1.5">
              <Label>dec (degrees) *</Label>
              <Input
                type="number"
                step="0.0001"
                bind:value={objectData.dec}
                required
              />
            </div>

            <div class="space-y-1.5">
              <Label>magnitude *</Label>
              <Input
                type="number"
                step="0.1"
                bind:value={objectData.mag}
                required
              />
            </div>

            <div class="space-y-1.5">
              <Label>type *</Label>
              <Input
                bind:value={objectData.type}
                placeholder="Galaxy, Nebula..."
                required
              />
            </div>

            <div class="space-y-1.5">
              <Label>size</Label>
              <Input bind:value={objectData.size} />
            </div>

            <div class="space-y-1.5">
              <Label>constellation</Label>
              <Input bind:value={objectData.constellation} />
            </div>

            <div class="space-y-1.5">
              <Label>catalog</Label>
              <Popover.Root bind:open={catalogOpen}>
                <Popover.Trigger asChild let:builder>
                  <Button
                    builders={[builder]}
                    variant="outline"
                    role="combobox"
                    aria-expanded={catalogOpen}
                    class="w-full justify-between hover:bg-neutral-800/60"
                  >
                    {selectedCatalog || "select catalog..."}
                    <ChevronsUpDownIcon
                      class="ml-2 h-4 w-4 shrink-0 opacity-50"
                    />
                  </Button>
                </Popover.Trigger>
                <Popover.Content
                  class="w-[260px] p-0 bg-neutral-900 border-white/60"
                  align="start"
                >
                  <Command.Root>
                    <Command.Input
                      placeholder="search catalog..."
                      class=" border-white/10"
                    />
                    <Command.List>
                      <Command.Empty>no catalog found.</Command.Empty>
                      <Command.Group>
                        {#each catalogs as catalog}
                          <Command.Item
                            value={catalog.value}
                            onSelect={() => {
                              objectData.catalog = catalog.value;
                              closeAndFocusCatalogTrigger();
                            }}
                          >
                            <CheckIcon
                              class={cn(
                                "mr-2 h-4 w-4",
                                objectData.catalog !== catalog.value &&
                                  "text-transparent",
                              )}
                            />
                            {catalog.label}
                          </Command.Item>
                        {/each}
                      </Command.Group>
                    </Command.List>
                  </Command.Root>
                </Popover.Content>
              </Popover.Root>
            </div>

            <div class="space-y-1.5">
              <Label>ngc</Label>
              <Input bind:value={objectData.ngc} />
            </div>
          </div>
        </div>
      {/if}
    </div>

    {#if searchPerformed}
      <div transition:slide={{ duration: 200 }}>
        <Dialog.Footer>
          <Button variant="outline" on:click={() => (open = false)}
            >cancel</Button
          >
          <Button
            on:click={handleSubmit}
            disabled={loading}
            class="bg-green-600 hover:bg-green-700 text-white"
          >
            {loading ? "saving..." : "save object"}
          </Button>
        </Dialog.Footer>
      </div>
    {/if}
  </Dialog.Content>
</Dialog.Root>
