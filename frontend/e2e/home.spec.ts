import { test, expect } from '@playwright/test'

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('displays the page title', async ({ page }) => {
    await expect(page.locator('[data-testid="home-page"]')).toBeVisible()
    await expect(page.locator('h1')).toContainText('Daily Digest')
  })

  test('displays the header with logo', async ({ page }) => {
    await expect(page.locator('[data-testid="logo-link"]')).toBeVisible()
    await expect(page.locator('[data-testid="logo-link"]')).toContainText('Daily Paper Report')
  })

  test('navigation links are visible and functional', async ({ page }) => {
    // Check navigation links exist
    await expect(page.locator('[data-testid="nav-today"]')).toBeVisible()
    await expect(page.locator('[data-testid="nav-archive"]')).toBeVisible()
    await expect(page.locator('[data-testid="nav-sources"]')).toBeVisible()
    await expect(page.locator('[data-testid="nav-status"]')).toBeVisible()

    // Navigate to Archive page
    await page.locator('[data-testid="nav-archive"]').click()
    await expect(page.locator('[data-testid="archive-page"]')).toBeVisible()

    // Navigate to Sources page
    await page.locator('[data-testid="nav-sources"]').click()
    await expect(page.locator('[data-testid="sources-page"]')).toBeVisible()

    // Navigate to Status page
    await page.locator('[data-testid="nav-status"]').click()
    await expect(page.locator('[data-testid="status-page"]')).toBeVisible()

    // Navigate back to Home
    await page.locator('[data-testid="nav-today"]').click()
    await expect(page.locator('[data-testid="home-page"]')).toBeVisible()
  })

  test('displays content sections', async ({ page }) => {
    // Wait for data to load (either content or empty states)
    await page.waitForSelector('[data-testid="section-top5"]')

    // Check all sections exist
    await expect(page.locator('[data-testid="section-top5"]')).toBeVisible()
    await expect(page.locator('[data-testid="section-models"]')).toBeVisible()
    await expect(page.locator('[data-testid="section-papers"]')).toBeVisible()
    await expect(page.locator('[data-testid="section-radar"]')).toBeVisible()
  })

  test('section headers have correct titles', async ({ page }) => {
    await page.waitForSelector('[data-testid="section-title-top5"]')

    await expect(page.locator('[data-testid="section-title-top5"]')).toContainText(
      'Top 5 Must-Read',
    )
    await expect(page.locator('[data-testid="section-title-models"]')).toContainText(
      'Model Releases',
    )
    await expect(page.locator('[data-testid="section-title-papers"]')).toContainText('Papers')
    await expect(page.locator('[data-testid="section-title-radar"]')).toContainText('Radar')
  })
})

test.describe('Sources Page', () => {
  test('displays source cards when data is available', async ({ page }) => {
    await page.goto('/sources')

    await expect(page.locator('[data-testid="sources-page"]')).toBeVisible()
    await expect(page.locator('h1')).toContainText('Sources')
  })
})

test.describe('Status Page', () => {
  test('displays system status information', async ({ page }) => {
    await page.goto('/status')

    await expect(page.locator('[data-testid="status-page"]')).toBeVisible()
    await expect(page.locator('h1')).toContainText('Status')
  })
})

test.describe('Archive Page', () => {
  test('displays archive placeholder', async ({ page }) => {
    await page.goto('/archive')

    await expect(page.locator('[data-testid="archive-page"]')).toBeVisible()
    await expect(page.locator('h1')).toContainText('Archive')
  })
})
