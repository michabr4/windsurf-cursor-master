import { z } from "zod";

export const MimirCompanyQuerySchema = z.object({
  companyId: z.string().trim().min(1).optional()
});
