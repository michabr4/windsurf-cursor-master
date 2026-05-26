import { z } from "zod";

export const SF_ID_PATTERN = /^[a-zA-Z0-9]{15,18}$/;

const sfId = z.string().regex(SF_ID_PATTERN, "Invalid Salesforce id format");

export const CreateCaseSchema = z.object({
  subject: z.string().trim().min(1).max(500),
  description: z.string().max(5000).optional(),
  priority: z.enum(["High", "Medium", "Low", "Critical"]).optional(),
  accountId: sfId.optional(),
  contactId: sfId.optional()
});

export const PatchCaseSchema = z
  .object({
    Status: z.string().max(100).optional(),
    Priority: z.enum(["High", "Medium", "Low", "Critical"]).optional(),
    Description: z.string().max(5000).optional(),
    Subject: z.string().max(500).optional()
  })
  .refine((body) => Object.values(body).some((v) => v !== undefined), {
    message: "No valid fields to update"
  });
