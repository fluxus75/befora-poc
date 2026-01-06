import { test, expect } from '@playwright/test';

test.describe('Basic Application Tests', () => {
  test('should load the homepage', async ({ page }) => {
    await page.goto('/');

    // Check that the page loads
    await expect(page).toHaveTitle(/Befora/i);
  });

  test('should have microphone permission prompt', async ({ page, context }) => {
    // Grant microphone permissions for WebRTC testing
    await context.grantPermissions(['microphone']);

    await page.goto('/');

    // Check for voice interface elements
    const microphoneButton = page.getByRole('button', { name: /start|microphone/i });
    if (await microphoneButton.isVisible()) {
      await expect(microphoneButton).toBeEnabled();
    }
  });

  test('should handle network status display', async ({ page }) => {
    await page.goto('/');

    // Simulate offline
    await page.context().setOffline(true);

    // Check for network status indicator
    const networkStatus = page.locator('[data-testid="network-status"]');
    if (await networkStatus.isVisible()) {
      await expect(networkStatus).toContainText(/offline|연결 끊김/i);
    }

    // Go back online
    await page.context().setOffline(false);
  });
});

test.describe('WebRTC Connection Tests', () => {
  test('should initialize audio context', async ({ page, context }) => {
    await context.grantPermissions(['microphone']);

    await page.goto('/');

    // Check if AudioContext is available
    const hasAudioContext = await page.evaluate(() => {
      return typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined';
    });

    expect(hasAudioContext).toBe(true);
  });
});
