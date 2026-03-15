import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: 'html',
  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    // In CI the frontend is pre-built by npm run build, so use `vite preview`
    // which serves the static dist/ folder instantly and binds explicitly to
    // 127.0.0.1.  Locally, use the live dev server as before.
    command: process.env.CI
      ? 'npm run preview -- --port 5173 --host 127.0.0.1'
      : 'npm run dev',
    url: 'http://127.0.0.1:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
})
