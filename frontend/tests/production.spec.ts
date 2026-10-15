import { test, expect } from "@playwright/test";
test("production static build serves every view, bundled font and recorded model trace", async ({
  page,
}) => {
  const failures: string[] = [];
  page.on("pageerror", (e) => failures.push(e.message));
  const response = await page.goto("/");
  expect(response?.status()).toBe(200);
  await expect(page.locator(".scoreboard")).toBeVisible();
  await expect(page.locator(".source-label")).toContainText(
    "Recorded Agent Run",
  );
  expect(
    await page.evaluate(() => document.fonts.check('14px "DM Sans Variable"')),
  ).toBeTruthy();
  for (const name of [
    "Analyst control room",
    "Your match",
    "Broadcast studio",
    "Agent intelligence",
    "Match recap",
  ]) {
    await page.getByRole("button", { name, exact: true }).click();
    await expect(page.locator(".page-heading")).toBeVisible();
  }
  expect(failures).toEqual([]);
});
