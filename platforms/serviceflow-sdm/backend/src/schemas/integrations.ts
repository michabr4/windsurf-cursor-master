import { z } from "zod";

export const WarRoomBodySchema = z.object({
  title: z.string().trim().max(200).optional()
});

export const SYNC_SOURCES = ["dna-center", "tac", "smart-licensing", "salesforce"] as const;

export const SyncSourceParamSchema = z.enum(SYNC_SOURCES);
