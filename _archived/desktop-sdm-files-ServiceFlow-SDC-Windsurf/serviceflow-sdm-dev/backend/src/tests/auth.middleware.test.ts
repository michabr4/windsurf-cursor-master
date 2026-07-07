import { describe, expect, it, vi } from "vitest";
import { requireRoles } from "../middleware/auth.js";

describe("requireRoles", () => {
  it("blocks forbidden role", () => {
    const middleware = requireRoles(["admin"]);
    const req = { auth: { role: "viewer" } } as any;
    const json = vi.fn();
    const status = vi.fn(() => ({ json }));
    const res = { status } as any;
    const next = vi.fn();

    middleware(req, res, next);

    expect(status).toHaveBeenCalledWith(403);
    expect(next).not.toHaveBeenCalled();
  });
});
