import { chromium } from "playwright";
import fs from "node:fs";

const url = process.argv[2] || "http://127.0.0.1:8080/";
const out = process.argv[3] || "/workspace/screenshots/sac-preview.png";
fs.mkdirSync("/workspace/screenshots", { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
await page.waitForTimeout(800);
const text = await page.locator("body").innerText();
await page.screenshot({ path: out, fullPage: true });
// mobile
await page.setViewportSize({ width: 390, height: 844 });
await page.waitForTimeout(300);
await page.screenshot({ path: out.replace(".png", "-mobile.png"), fullPage: true });
console.log(JSON.stringify({
  url,
  text_len: text.length,
  has_title: text.includes("System Architecture Capture"),
  has_overview: /Reverse-engineer|Overview|Northstar/i.test(text),
  errors: errors.slice(0, 10),
  screenshot: out,
}, null, 2));
if (!text.includes("System Architecture Capture") || text.length < 100) {
  process.exit(2);
}
if (errors.some((e) => /Failed to load module|Uncaught/i.test(e))) {
  process.exit(3);
}
await browser.close();
