<script lang="ts">
  import "../app.css";
  import { onMount } from "svelte";
  import Starback from "starback";
  import Sonner from "$lib/components/ui/sonner/sonner.svelte";

  let canvas: HTMLCanvasElement;

  onMount(() => {
    const starback = new Starback(canvas, {
      type: "dot",
      quantity: 100,
      direction: 180,
      backgroundColor: "#000000",
      starSize: [0, 1],
      speed: [0.1, 0.2],
      randomOpacity: true,
    });
  });
</script>

<canvas
  bind:this={canvas}
  class="fixed inset-0 w-full h-full z-0 pointer-events-none"
></canvas>
<slot />
<Sonner
  position="bottom-right"
  style="background: rgba(0, 0, 0, 0.8); border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(12px); color: #fff; border-radius: 0px;"
/>
