<script lang="ts">
  import { Input } from "$lib/components/ui/input";

  export let date: string; // ISO String YYYY-MM-DD

  // For now, we are styling the native picker to look "shadcn-like" / minimalist
  // because building a full custom calendar from scratch in this prompt might be overkill
  // and maintaining accessibility is hard. A styled native picker is robust.
</script>

<div class="relative group">
  <div
    class="absolute inset-y-0 left-0 pl-0 flex items-center pointer-events-none"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="text-zinc-500"
      ><rect width="18" height="18" x="3" y="4" rx="2" ry="2" /><line
        x1="16"
        x2="16"
        y1="2"
        y2="6"
      /><line x1="8" x2="8" y1="2" y2="6" /><line
        x1="3"
        x2="21"
        y1="10"
        y2="10"
      /></svg
    >
  </div>
  <Input
    type="date"
    bind:value={date}
    class="border-0 border-b border-neutral-700 rounded-none pl-8 px-0 text-xl font-mono focus:border-white [&::-webkit-calendar-picker-indicator]:invert [&::-webkit-calendar-picker-indicator]:opacity-50 [&::-webkit-calendar-picker-indicator]:hover:opacity-100 [&::-webkit-calendar-picker-indicator]:cursor-pointer"
  />
</div>
