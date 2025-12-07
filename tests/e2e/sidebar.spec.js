// @ts-check
const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  await page.goto('/'); // Base URL is configured in playwright.config.js
});

test('sidebar has intro link', async ({ page }) => {
  const introLink = page.locator('a', { hasText: 'Intro' }).first();
  await expect(introLink).toBeVisible();
  await expect(introLink).toHaveAttribute('href', '/docs/intro');
});

test('sidebar has tutorial category', async ({ page }) => {
  const tutorialCategory = page.locator('.menu__list-item-collapsible', { hasText: 'Tutorial' }).first();
  await expect(tutorialCategory).toBeVisible();
});

test('sidebar has "Create a Document" link', async ({ page }) => {
  // First, expand the 'Tutorial' category if it's collapsed
  const tutorialCategory = page.locator('.menu__list-item-collapsible', { hasText: 'Tutorial' }).first();
  const isCollapsed = await tutorialCategory.locator('.menu__list-item--collapsed').count();
  if (isCollapsed) {
    await tutorialCategory.click(); // Click to expand
  }

  const createDocLink = page.locator('a', { hasText: 'Create a Document' }).first();
  await expect(createDocLink).toBeVisible();
  await expect(createDocLink).toHaveAttribute('href', '/docs/tutorial-basics/create-a-document');
});
