import { describe, it, expect } from "vitest";
import { localCorrelate } from "./detection";
import { eventFeatures, evaluate } from "./laboratory";
import fixtures from "../generated/parity.json";
describe("Python/browser detection and feature parity", () => {
  for (const [index, f] of fixtures.entries())
    it("matches Python fixture " + index, () => {
      expect(
        localCorrelate(f.events).map((i) => ({
          id: i.id,
          rule: i.rule,
          severity: i.severity,
          evidence: i.evidence,
        })),
      ).toEqual(f.incidents);
      expect(eventFeatures(f.events)).toEqual(f.features);
    });
});
it("recomputes metrics on all 500 held-out rows", () => {
  const a = evaluate();
  expect(
    a.confusion_matrix.flat().reduce((x: number, y: number) => x + y, 0),
  ).toBe(500);
  expect(a.f1).toBeGreaterThan(0);
  expect(evaluate(0.5).recall).toBeGreaterThanOrEqual(evaluate(2).recall);
});
