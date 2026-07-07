import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Local dev: /project-dashboard/  |  GitHub Pages: /windsurf-cursor-master/project-dashboard/
export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE_URL ?? '/project-dashboard/',
})
