import { test, expect } from "@playwright/test";
test("real match corpus, all eight main competitions and season exclusion", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("button", { name: "Real match lab", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Historical match explorer" }),
  ).toBeVisible();
  await expect(page.locator(".history-metrics")).toContainText("12,372");
  await expect(page.locator(".scoreboard")).toHaveCount(0);
  expect(
    await page
      .getByLabel("Historical season")
      .locator("option")
      .allTextContents(),
  ).not.toContain("2026-27");
  for (const [code, count] of [
    ["en.1", "380"],
    ["de.1", "306"],
    ["es.1", "380"],
    ["it.1", "380"],
    ["fr.1", "306"],
    ["uefa.cl", "189"],
    ["uefa.el", "189"],
    ["uefa.conf", "153"],
  ]) {
    await page.getByLabel("Real competition").selectOption(code);
    await expect(page.locator(".history-pages")).toContainText(
      `${count} fixtures`,
    );
    await expect(page.locator(".history-table tbody tr")).toHaveCount(30);
  }
  await page.locator(".history-table tbody button").first().click();
  await expect(
    page.getByRole("dialog", { name: "Real match details" }),
  ).toContainText("held-out walk-forward");
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.screenshot({
    path: "../docs/screenshots/07-real-match-lab.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 900 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
});
test("one local server opens UI and API, auto-connects and actually recomputes historical model", async ({
  page,
}) => {
  await page.goto("http://127.0.0.1:8000/");
  await expect(
    page.getByRole("button", { name: "Local backend connected", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Real match lab", exact: true })
    .click();
  await expect(page.locator(".history-table tbody tr")).toHaveCount(30);
  await page.locator(".history-table tbody button").first().click();
  const response = page.waitForResponse(
    (r) => r.url().includes("/api/history/prediction/") && r.status() === 200,
  );
  await page
    .getByRole("button", { name: "Run trained model on backend" })
    .click();
  expect((await (await response).json()).model_variant).toBe("evaluation");
  await page.keyboard.press("Escape");
  await page.screenshot({path:"../docs/screenshots/08-single-server-proof.png",fullPage:false});
});
