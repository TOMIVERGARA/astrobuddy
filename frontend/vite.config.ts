import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
    plugins: [sveltekit()],
    server: {
        fs: {
            strict: false
        },
        watch: {
            usePolling: true
        },
        hmr: {
            clientPort: 5173
        }
    },
    // Deshabilitar caché de deps para evitar problemas en Docker
    cacheDir: '/tmp/.vite'
});
