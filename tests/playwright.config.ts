import { defineConfig } from '@playwright/test';
import { sharedPlaywrightConfig } from '@ov-integrations/playwright-framework';

export default defineConfig({
  ...sharedPlaywrightConfig,
  testDir: './specs',
  use: {
    ...sharedPlaywrightConfig.use,
    baseURL: process.env.UI_TEST_WEB_URL,
  },
  expect: {
    ...sharedPlaywrightConfig.expect,
    timeout: 15_000,
  },
});
