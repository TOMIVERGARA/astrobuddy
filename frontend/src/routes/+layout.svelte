<script lang="ts">
  import "../app.css";
  import { onMount } from "svelte";
  import Starback from "starback";

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
