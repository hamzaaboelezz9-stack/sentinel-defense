import React from "react";
import { it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ResponseAssistant } from "./ResponseAssistant";
vi.mock("../services/api", () => ({
  api: vi.fn(async () => ({
    version: "2.0",
    summary: "Brute force review",
    confidence: "Rule match only",
    benign_explanations: ["Service retry"],
    investigate: ["Inspect source"],
    containment: ["Human approval required"],
    impact: ["May affect services"],
    recovery: ["Restore approved settings"],
    verify: ["Review new evidence"],
    closure: ["Record decision"],
  })),
}));
it("shows auditable recommendations and records only a human decision", async () => {
  const record = vi.fn();
  render(<ResponseAssistant incident={{ id: "case-1" }} onRecord={record} />);
  expect(await screen.findByText("Brute force review")).toBeInTheDocument();
  expect(screen.getByText("Human approval required")).toBeInTheDocument();
  fireEvent.click(
    screen.getByRole("button", { name: "Record analyst decision →" }),
  );
  expect(record).toHaveBeenCalledOnce();
});
