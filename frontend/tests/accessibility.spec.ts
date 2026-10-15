import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { writeFile } from "node:fs/promises";
test("all views expose usable accessible names and no serious axe violations", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.locator(".scoreboard")).toBeVisible();
  const reports = [];
  for (const name of [
    "Live intelligence",
    "Analyst control room",
    "Your match",
    "Broadcast studio",
    "Agent intelligence",
    "Match recap",
    "Real match lab",
  ]) {
    await page.getByRole("button", { name, exact: true }).click();
    const result = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();
    reports.push({ view: name, violations: result.violations });
  }
  await writeFile(
    "../docs/reports/accessibility.json",
    JSON.stringify(reports, null, 2),
  );
  const serious = reports.flatMap((r) =>
    r.violations
      .filter((v) => ["serious", "critical"].includes(v.impact || ""))
      .map((v) => `${r.view}: ${v.id} (${v.nodes.length} nodes)`),
  );
  expect(serious).toEqual([]);
});
