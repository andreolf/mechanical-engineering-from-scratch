import { defineConfig } from 'vite';
import { resolve } from 'node:path';
export default defineConfig({
  base: './',
  build: { outDir: 'dist', chunkSizeWarningLimit: 900, rollupOptions: { input: { main: resolve(import.meta.dirname, 'index.html'), learn: resolve(import.meta.dirname, 'learn.html') } } },
  server: { port: 5183 },
  preview: { port: 4183 },
});
