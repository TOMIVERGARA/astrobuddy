<script lang="ts">
  import { onMount } from "svelte";
  import { getApiUrl } from "$lib/config";
  import { Button } from "$lib/components/ui/button";
  import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
  } from "$lib/components/ui/card";
  import * as AlertDialog from "$lib/components/ui/alert-dialog";
  import { toast } from "svelte-sonner";
  import Database from "lucide-svelte/icons/database";
  import Download from "lucide-svelte/icons/download";
  import Upload from "lucide-svelte/icons/upload";
  import RefreshCw from "lucide-svelte/icons/refresh-cw";
  import ArrowLeft from "lucide-svelte/icons/arrow-left";
  import { goto } from "$app/navigation";

  const API_URL = getApiUrl();

  let stats = {
    total_objects: 0,
    by_catalog: {} as Record<string, number>,
    by_type: {} as Record<string, number>,
  };

  let loading = false;
  let showSeedDialog = false;
  let showImportDialog = false;
  let importFile: File | null = null;
  let replaceDatabase = false;

  onMount(() => {
    loadStats();
  });

  async function loadStats() {
    try {
      const response = await fetch(`${API_URL}/admin/stats`);
      if (!response.ok) throw new Error("Failed to load stats");
      stats = await response.json();
    } catch (error) {
      console.error("Error loading stats:", error);
      toast.error("Failed to load database statistics");
    }
  }

  async function handleSeedMessier() {
    loading = true;
    showSeedDialog = false;

    try {
      toast.info("Seeding Messier catalog...");
      const response = await fetch(`${API_URL}/admin/seed-messier`, {
        method: "POST",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to seed catalog");
      }

      const result = await response.json();

      if (result.success) {
        toast.success(
          `Catalog seeded successfully: ${result.inserted} objects inserted, ${result.skipped} skipped`,
        );
        await loadStats();
      } else {
        toast.error(`Error: ${result.error}`);
      }
    } catch (error: any) {
      console.error("Error seeding Messier:", error);
      toast.error(error.message || "Failed to seed Messier catalog");
    } finally {
      loading = false;
    }
  }

  async function handleExport() {
    loading = true;

    try {
      toast.info("Exporting database...");
      const response = await fetch(`${API_URL}/admin/export`);

      if (!response.ok) {
        throw new Error("Failed to export database");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      // Extract filename from Content-Disposition header or use default
      const contentDisposition = response.headers.get("Content-Disposition");
      const filename = contentDisposition
        ? contentDisposition.split("filename=")[1]?.replace(/"/g, "")
        : `astrobuddy-backup-${new Date().toISOString().split("T")[0]}.json`;

      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success("Database exported successfully");
    } catch (error: any) {
      console.error("Error exporting database:", error);
      toast.error("Failed to export database");
    } finally {
      loading = false;
    }
  }

  function handleFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      importFile = target.files[0];
    }
  }

  async function handleImport() {
    if (!importFile) {
      toast.error("Please select a JSON file");
      return;
    }

    loading = true;
    showImportDialog = false;

    try {
      toast.info("Importing database...");

      const fileContent = await importFile.text();
      const objects = JSON.parse(fileContent);

      if (!Array.isArray(objects)) {
        throw new Error("JSON file must contain an array of objects");
      }

      const response = await fetch(`${API_URL}/admin/import`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          objects: objects,
          replace: replaceDatabase,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to import database");
      }

      const result = await response.json();

      if (result.success) {
        toast.success(
          `Database imported: ${result.inserted} objects inserted, ${result.skipped} skipped`,
        );
        await loadStats();
        importFile = null;
        replaceDatabase = false;
      } else {
        toast.error(`Error: ${result.error}`);
      }
    } catch (error: any) {
      console.error("Error importing database:", error);
      toast.error(error.message || "Failed to import database");
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen relative z-10">
  <div class="container mx-auto px-4 py-8 max-w-6xl">
    <!-- Header -->
    <div class="flex items-center gap-4 mb-8">
      <Button
        variant="ghost"
        size="icon"
        on:click={() => goto("/")}
        class="text-white hover:bg-white/10"
      >
        <ArrowLeft class="h-5 w-5" />
      </Button>
      <div>
        <h1 class="text-4xl font-bold text-white mb-2">Administration</h1>
        <p class="text-gray-400">Celestial objects database management</p>
      </div>
    </div>

    <!-- Stats Card -->
    <Card class="border-white/10 mb-8">
      <CardHeader>
        <CardTitle class="text-white flex items-center gap-2">
          <Database class="h-5 w-5" />
          Database Statistics
        </CardTitle>
        <CardDescription class="text-gray-400">
          Current catalog status
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Total Objects -->
          <div class="bg-white/5 p-4 rounded-lg">
            <div class="text-gray-400 text-sm mb-1">Total Objects</div>
            <div class="text-3xl font-bold text-white">
              {stats.total_objects}
            </div>
          </div>

          <!-- By Catalog -->
          <div class="bg-white/5 p-4 rounded-lg">
            <div class="text-gray-400 text-sm mb-2">By Catalog</div>
            {#if Object.keys(stats.by_catalog).length > 0}
              <div class="space-y-1">
                {#each Object.entries(stats.by_catalog) as [catalog, count]}
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-300">{catalog || "No catalog"}:</span
                    >
                    <span class="text-white font-semibold">{count}</span>
                  </div>
                {/each}
              </div>
            {:else}
              <div class="text-gray-500 text-sm">No data</div>
            {/if}
          </div>

          <!-- By Type -->
          <div class="bg-white/5 p-4 rounded-lg">
            <div class="text-gray-400 text-sm mb-2">By Type</div>
            {#if Object.keys(stats.by_type).length > 0}
              <div class="space-y-1 max-h-32 overflow-y-auto">
                {#each Object.entries(stats.by_type) as [type, count]}
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-300">{type}:</span>
                    <span class="text-white font-semibold">{count}</span>
                  </div>
                {/each}
              </div>
            {:else}
              <div class="text-gray-500 text-sm">No data</div>
            {/if}
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Action Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Seed Messier Card -->
      <Card class="border-white/10">
        <CardHeader>
          <CardTitle class="text-white flex items-center gap-2">
            <RefreshCw class="h-5 w-5" />
            Seed Messier
          </CardTitle>
          <CardDescription class="text-gray-400">
            Import Messier catalog (110 objects)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p class="text-gray-300 text-sm mb-4">
            This will replace all existing Messier catalog objects with fresh
            data from the JSON file.
          </p>
          <Button
            class="w-full bg-blue-600 hover:bg-blue-700"
            disabled={loading}
            on:click={() => (showSeedDialog = true)}
          >
            <RefreshCw class="h-4 w-4 mr-2" />
            Seed Catalog
          </Button>
        </CardContent>
      </Card>

      <!-- Export Card -->
      <Card class="border-white/10">
        <CardHeader>
          <CardTitle class="text-white flex items-center gap-2">
            <Download class="h-5 w-5" />
            Export Database
          </CardTitle>
          <CardDescription class="text-gray-400">
            Download complete backup as JSON
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p class="text-gray-300 text-sm mb-4">
            Download all database objects in JSON format for backup or
            migration.
          </p>
          <Button
            class="w-full bg-green-600 hover:bg-green-700"
            disabled={loading}
            on:click={handleExport}
          >
            <Download class="h-4 w-4 mr-2" />
            Download Backup
          </Button>
        </CardContent>
      </Card>

      <!-- Import Card -->
      <Card class="border-white/10">
        <CardHeader>
          <CardTitle class="text-white flex items-center gap-2">
            <Upload class="h-5 w-5" />
            Import Database
          </CardTitle>
          <CardDescription class="text-gray-400">
            Restore from JSON file
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p class="text-gray-300 text-sm mb-4">
            Import objects from a JSON backup file. You can choose to replace or
            add to existing data.
          </p>
          <div class="space-y-3">
            <input
              type="file"
              accept=".json"
              on:change={handleFileSelect}
              class="w-full text-sm text-gray-400
                file:mr-4 file:py-2 file:px-4
                file:rounded-lg file:border-0
                file:text-sm file:font-semibold
                file:bg-white/10 file:text-white
                hover:file:bg-white/20 file:cursor-pointer"
            />
            <Button
              class="w-full bg-orange-600 hover:bg-orange-700"
              disabled={loading || !importFile}
              on:click={() => (showImportDialog = true)}
            >
              <Upload class="h-4 w-4 mr-2" />
              Import Data
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</div>

<!-- Seed Confirmation Dialog -->
<AlertDialog.Root bind:open={showSeedDialog}>
  <AlertDialog.Content class="border-white/10">
    <AlertDialog.Header>
      <AlertDialog.Title class="text-white">
        Confirm Messier Catalog Seeding?
      </AlertDialog.Title>
      <AlertDialog.Description class="text-gray-400">
        This action will remove all existing Messier catalog objects from the
        database and replace them with data from the JSON file. Objects from
        other catalogs will not be affected.
      </AlertDialog.Description>
    </AlertDialog.Header>
    <AlertDialog.Footer>
      <AlertDialog.Cancel class="bg-white/10 text-white hover:bg-white/20">
        Cancel
      </AlertDialog.Cancel>
      <AlertDialog.Action
        class="bg-blue-600 hover:bg-blue-700"
        on:click={handleSeedMessier}
      >
        Confirm Seed
      </AlertDialog.Action>
    </AlertDialog.Footer>
  </AlertDialog.Content>
</AlertDialog.Root>

<!-- Import Confirmation Dialog -->
<AlertDialog.Root bind:open={showImportDialog}>
  <AlertDialog.Content class="border-white/10">
    <AlertDialog.Header>
      <AlertDialog.Title class="text-white">
        Confirm Database Import?
      </AlertDialog.Title>
      <AlertDialog.Description class="text-gray-400 space-y-3">
        <p>
          You are about to import objects from the file:
          <strong class="text-white block mt-1">{importFile?.name}</strong>
        </p>

        <div class="bg-white/5 p-3 rounded-lg">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              bind:checked={replaceDatabase}
              class="w-4 h-4 rounded border-gray-600 bg-white/10
                     text-orange-600 focus:ring-orange-500 focus:ring-offset-0"
            />
            <span class="text-gray-300 text-sm">
              Replace entire database (deletes all existing objects)
            </span>
          </label>
        </div>

        {#if replaceDatabase}
          <div class="bg-red-900/20 border border-red-800 rounded-lg p-3">
            <p class="text-red-400 text-sm font-semibold">
              ⚠️ WARNING: This action will permanently delete all current
              objects from the database before importing. Make sure you have a
              backup.
            </p>
          </div>
        {:else}
          <p class="text-gray-400 text-sm">
            Objects will be added or updated in the database without deleting
            existing data.
          </p>
        {/if}
      </AlertDialog.Description>
    </AlertDialog.Header>
    <AlertDialog.Footer>
      <AlertDialog.Cancel class="bg-white/10 text-white hover:bg-white/20">
        Cancel
      </AlertDialog.Cancel>
      <AlertDialog.Action
        class="bg-orange-600 hover:bg-orange-700"
        on:click={handleImport}
      >
        Confirm Import
      </AlertDialog.Action>
    </AlertDialog.Footer>
  </AlertDialog.Content>
</AlertDialog.Root>
