import { defineConfig } from 'vite';
export default defineConfig({ base: './', build: { outDir: 'dist', chunkSizeWarningLimit: 900 }, server: { port: 5183 }, preview: { port: 4183 } });
