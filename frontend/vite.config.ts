import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Backend origin: change if your API runs elsewhere (default dev port 8010).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://localhost:8010", changeOrigin: true },
    },
  },
});
