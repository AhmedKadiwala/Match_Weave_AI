import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./deployment-tests",
  timeout: 30000,
  workers: 1,
  reporter: [
    ["list"],
    ["json", { outputFile: "../docs/reports/render-browser-tests.json" }],
  ],
  use: {
    baseURL: "http://127.0.0.1:4173",
    viewport: { width: 1440, height: 1000 },
    headless: true,
  },
});
