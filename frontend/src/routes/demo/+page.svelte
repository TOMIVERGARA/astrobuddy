<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { Input } from "$lib/components/ui/input";
  import { Label } from "$lib/components/ui/label";
  import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
  } from "$lib/components/ui/card";
  import {
    ToggleGroup,
    ToggleGroupItem,
  } from "$lib/components/ui/toggle-group";
</script>

<div
  class="min-h-screen bg-gradient-to-br from-neutral-950 via-neutral-900 to-neutral-950 text-white p-8"
>
  <div class="max-w-4xl mx-auto space-y-12">
    <!-- Header -->
    <header class="space-y-2">
      <h1 class="text-4xl font-bold lowercase tracking-tight">shadcn-svelte</h1>
      <p class="text-muted-foreground lowercase">
        minimalist aesthetic components
      </p>
    </header>

    <!-- Buttons Section -->
    <Card>
      <CardHeader>
        <CardTitle class="lowercase">buttons</CardTitle>
        <CardDescription class="lowercase"
          >different button variants</CardDescription
        >
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="flex flex-wrap gap-3">
          <Button>default button</Button>
          <Button variant="destructive">destructive</Button>
          <Button variant="outline">outline</Button>
          <Button variant="secondary">secondary</Button>
          <Button variant="ghost">ghost</Button>
          <Button variant="link">link</Button>
        </div>

        <div class="flex flex-wrap gap-3">
          <Button size="sm">small</Button>
          <Button size="default">default</Button>
          <Button size="lg">large</Button>
          <Button size="icon">🚀</Button>
        </div>

        <div class="flex gap-3">
          <Button disabled>disabled button</Button>
        </div>
      </CardContent>
    </Card>

    <!-- Inputs Section -->
    <Card>
      <CardHeader>
        <CardTitle class="lowercase">inputs</CardTitle>
        <CardDescription class="lowercase"
          >text input components</CardDescription
        >
      </CardHeader>
      <CardContent class="space-y-6">
        <div class="space-y-2">
          <Label for="email">email address</Label>
          <Input id="email" type="email" placeholder="your@email.com" />
        </div>

        <div class="space-y-2">
          <Label for="password">password</Label>
          <Input id="password" type="password" placeholder="••••••••" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="number">number</Label>
            <Input id="number" type="number" placeholder="123" />
          </div>
          <div class="space-y-2">
            <Label for="date">date</Label>
            <Input id="date" type="date" />
          </div>
        </div>

        <div class="space-y-2">
          <Label for="disabled">disabled input</Label>
          <Input id="disabled" disabled value="cannot edit" />
        </div>
      </CardContent>
    </Card>

    <!-- Toggle Group Section -->
    <Card>
      <CardHeader>
        <CardTitle class="lowercase">toggle group</CardTitle>
        <CardDescription class="lowercase">selection controls</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="space-y-2">
          <Label>telescope type</Label>
          <ToggleGroup type="single" value="refractor">
            <ToggleGroupItem value="reflector" class="flex-1"
              >Reflector</ToggleGroupItem
            >
            <ToggleGroupItem value="refractor" class="flex-1"
              >Refractor</ToggleGroupItem
            >
            <ToggleGroupItem value="maksutov" class="flex-1"
              >Maksutov</ToggleGroupItem
            >
          </ToggleGroup>
        </div>

        <div class="space-y-2">
          <Label>viewing mode</Label>
          <ToggleGroup type="single" value="dark">
            <ToggleGroupItem value="light" class="flex-1">Light</ToggleGroupItem
            >
            <ToggleGroupItem value="dark" class="flex-1">Dark</ToggleGroupItem>
            <ToggleGroupItem value="auto" class="flex-1">Auto</ToggleGroupItem>
          </ToggleGroup>
        </div>
      </CardContent>
    </Card>

    <!-- Cards Section -->
    <div class="grid md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle class="lowercase">observation 01</CardTitle>
          <CardDescription class="lowercase"
            >messier 42 - orion nebula</CardDescription
          >
        </CardHeader>
        <CardContent>
          <p class="text-sm text-muted-foreground lowercase">
            a stellar nursery located in the orion constellation. best viewed
            during winter months.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle class="lowercase">observation 02</CardTitle>
          <CardDescription class="lowercase"
            >messier 31 - andromeda galaxy</CardDescription
          >
        </CardHeader>
        <CardContent>
          <p class="text-sm text-muted-foreground lowercase">
            the nearest spiral galaxy to the milky way. visible to the naked eye
            in dark skies.
          </p>
        </CardContent>
      </Card>
    </div>

    <!-- Form Example -->
    <Card>
      <CardHeader>
        <CardTitle class="lowercase">complete form</CardTitle>
        <CardDescription class="lowercase"
          >example of combined components</CardDescription
        >
      </CardHeader>
      <CardContent class="space-y-6">
        <div class="grid md:grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="firstname">first name</Label>
            <Input id="firstname" placeholder="john" />
          </div>
          <div class="space-y-2">
            <Label for="lastname">last name</Label>
            <Input id="lastname" placeholder="doe" />
          </div>
        </div>

        <div class="space-y-2">
          <Label>experience level</Label>
          <ToggleGroup type="single" value="intermediate">
            <ToggleGroupItem value="beginner" class="flex-1"
              >Beginner</ToggleGroupItem
            >
            <ToggleGroupItem value="intermediate" class="flex-1"
              >Intermediate</ToggleGroupItem
            >
            <ToggleGroupItem value="advanced" class="flex-1"
              >Advanced</ToggleGroupItem
            >
          </ToggleGroup>
        </div>

        <div class="space-y-2">
          <Label for="notes">observation notes</Label>
          <Input id="notes" placeholder="enter your notes..." />
        </div>

        <div class="flex gap-3 pt-4">
          <Button class="flex-1">save observation</Button>
          <Button variant="outline">cancel</Button>
        </div>
      </CardContent>
    </Card>

    <!-- Footer -->
    <footer
      class="text-center text-xs text-muted-foreground lowercase pt-8 border-t border-neutral-800"
    >
      shadcn-svelte components with minimalist aesthetic • astrobuddy
    </footer>
  </div>
</div>
