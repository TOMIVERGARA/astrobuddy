<script lang="ts">
  import { AnimatePresence, Motion } from "svelte-motion";
  import LoaderCore from "./LoaderCore.svelte";

  type LoadingState = {
    text: string;
  };

  export let loadingStates: LoadingState[];
  export let loading: boolean | undefined = undefined;
  export let currentStep: number = 0;
</script>

<AnimatePresence show={true}>
  {#if loading}
    <Motion
      let:motion
      initial={{
        opacity: 0,
      }}
      animate={{
        opacity: 1,
      }}
      exit={{
        opacity: 0,
      }}
    >
      <div
        use:motion
        class="fixed inset-0 z-[100] flex h-full w-full items-center justify-center backdrop-blur-xl bg-black/80"
      >
        <div class="relative h-96">
          <LoaderCore value={currentStep} {loadingStates} />
        </div>
      </div>
    </Motion>
  {/if}
</AnimatePresence>
