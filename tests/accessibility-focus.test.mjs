import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("keyboard focus outlines cover links and common interactive controls", async () => {
  const css = await readFile(new URL("../styles.css", import.meta.url), "utf8");
  const rule = css.match(/:where\(a,button,input,select,textarea\):focus-visible\s*\{[^}]+\}/);
  assert.ok(rule, "shared :focus-visible rule should include all common interactive controls");
  assert.match(rule[0], /outline:\s*3px solid\s+#?[\da-f]{6}/i);
  assert.match(rule[0], /outline-offset:\s*2px/);
});
