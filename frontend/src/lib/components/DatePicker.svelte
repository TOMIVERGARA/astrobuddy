<script lang="ts">
  import { Input } from "$lib/components/ui/input";

  export let date: string; // ISO String YYYY-MM-DD

  // For now, we are styling the native picker to look "shadcn-like" / minimalist
  // because building a full custom calendar from scratch in this prompt might be overkill
  // and maintaining accessibility is hard. A styled native picker is robust.
</script>

<div class="relative group">
  <Input
    type="date"
    bind:value={date}
    class="border-0 border-b border-neutral-700 rounded-none px-0 text-xl font-mono focus:border-white [&::-webkit-calendar-picker-indicator]:invert [&::-webkit-calendar-picker-indicator]:opacity-50 [&::-webkit-calendar-picker-indicator]:hover:opacity-100 [&::-webkit-calendar-picker-indicator]:cursor-pointer"
  />
</div>
