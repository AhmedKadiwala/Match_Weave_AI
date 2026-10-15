import { test, expect } from "@playwright/test";
test("configured frontend auto-connects to actual minimal Render-profile backend", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Render backend connected", exact: true }),
  ).toBeVisible();
  await expect(page.getByText("HOSTED API", { exact: true })).toBeVisible();
  await page
    .getByRole("button", { name: "Agent intelligence", exact: true })
    .click();
  await expect(
    page.getByLabel("Inference provider").locator('option[value="local"]'),
  ).toBeDisabled();
  await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  await expect(
    page.getByText("Fresh hosted workflow", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Real match lab", exact: true })
    .click();
  await page.getByLabel("Real competition").selectOption("uefa.cl");
  await expect(page.locator(".history-pages")).toContainText("189 fixtures");
  await page.locator(".history-table tbody button").first().click();
  const result = page.waitForResponse(
    (r) => r.url().includes("/api/history/prediction/") && r.status() === 200,
  );
  await page
    .getByRole("button", { name: "Run trained model on backend" })
    .click();
  expect((await (await result).json()).model_variant).toBe("evaluation");
});
