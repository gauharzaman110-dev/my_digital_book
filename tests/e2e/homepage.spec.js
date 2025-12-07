// @ts-check
const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  await page.goto('/'); // Base URL is configured in playwright.config.js
});

test('has title', async ({ page }) => {
  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/My Digital Book/);
});

test('has hero section', async ({ page }) => {
  const heroTitle = page.locator('.hero__title');
  await expect(heroTitle).toBeVisible();
  await expect(heroTitle).toContainText('My Digital Book');
});

test('has tagline', async ({ page }) => {
  const tagline = page.locator('.hero__subtitle');
  await expect(tagline).toBeVisible();
  await expect(tagline).toContainText('Dinosaurs are cool'); // From docusaurus.config.ts
});
