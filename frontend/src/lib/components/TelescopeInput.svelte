<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import {
    ToggleGroup,
    ToggleGroupItem,
  } from "$lib/components/ui/toggle-group";
  import { Input } from "$lib/components/ui/input";
  import { Label } from "$lib/components/ui/label";

  // Props for binding
  export let aperture: number = 200;
  export let focalLength: number = 1200;
  export let type: "reflector" | "refractor" | "maksutov" = "reflector";

  const dispatch = createEventDispatcher();

  // Computed value to emulate the old single-string input for backend compatibility
  $: fullSpecString = `${type} ${aperture}mm ${focalLength}mm`;

  function dispatchChange() {
    dispatch("change", fullSpecString);
  }

  $: if (aperture || focalLength || type) {
    dispatchChange();
  }
</script>

<div class="space-y-4">
  <!-- Type Selector (Toggle Group) -->
  <ToggleGroup bind:value={type} type="single" class="w-full">
    <ToggleGroupItem value="reflector" class="flex-1">Reflector</ToggleGroupItem
    >
    <ToggleGroupItem value="refractor" class="flex-1">Refractor</ToggleGroupItem
    >
    <ToggleGroupItem value="maksutov" class="flex-1">Maksutov</ToggleGroupItem>
  </ToggleGroup>

  <!-- Numeric Inputs -->
  <div class="grid grid-cols-2 gap-4">
    <div class="space-y-2">
      <Label
        for="aperture"
        class="text-xs text-zinc-500 uppercase font-bold tracking-widest"
      >
        Aperture (mm)
      </Label>
      <Input
        id="aperture"
        type="number"
        bind:value={aperture}
        class="border-0 border-b border-neutral-700 rounded-none px-0 text-sm font-mono focus:border-white"
      />
    </div>
    <div class="space-y-2">
      <Label
        for="focallength"
        class="text-xs text-zinc-500 uppercase font-bold tracking-widest"
      >
        Focal Length (mm)
      </Label>
      <Input
        id="focallength"
        type="number"
        bind:value={focalLength}
        class="border-0 border-b border-neutral-700 rounded-none px-0 text-sm font-mono focus:border-white"
      />
    </div>
  </div>
</div>
