import { expect, test } from "@playwright/test";

test("console loads the queue and shows resolutions", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "AgentDesk Console" })).toBeVisible();
  await expect(page.getByRole("button", { name: /Queue/ })).toBeVisible();
  // the seeded queue has at least one card
  await expect(page.locator(".card").first()).toBeVisible();
});

test("an escalation can be approved by a human", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: /Escalations/ }).click();
  const firstCard = page.locator(".card").first();
  await expect(firstCard).toBeVisible();
  await firstCard.getByRole("button", { name: "Approve" }).click();
  // once approved the request leaves the escalations list and is resolved
  await page.getByRole("button", { name: /Queue/ }).click();
  await expect(page.getByText(/human approve/).first()).toBeVisible();
});
