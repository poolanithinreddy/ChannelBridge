import { expect, test } from "@playwright/test";
test("operator reviews live partner integration data", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill("operator@channelbridge.local");
  await page.getByLabel("Password").fill("ChannelBridgeDemo!");
  await page.getByRole("button", { name: "Enter workspace" }).click();
  await expect(
    page.getByRole("heading", { name: /Good morning, Morgan/ }),
  ).toBeVisible();
  await expect(page.getByText("Active partners")).toBeVisible();
  await page.getByRole("link", { name: "Partners", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Partner portfolio" }),
  ).toBeVisible();
  await page.getByRole("link", { name: /Northstar Media/ }).click();
  await expect(
    page.getByRole("heading", { name: "Northstar Media" }),
  ).toBeVisible();
  await expect(page.getByText("Readiness calculation")).toBeVisible();
});
