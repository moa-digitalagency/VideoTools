import { z } from "zod";

export const videoFileSchema = z.object({
  id: z.string(),
  filename: z.string(),
  originalName: z.string(),
  size: z.number(),
  duration: z.number().optional(),
  path: z.string(),
  createdAt: z.number(),
});

export type VideoFile = z.infer<typeof videoFileSchema>;

export const splitRequestSchema = z.object({
  videoId: z.string(),
  segmentDuration: z.number().min(1).max(3600),
});

export type SplitRequest = z.infer<typeof splitRequestSchema>;

export const mergeRequestSchema = z.object({
  videoIds: z.array(z.string()).min(2),
});

export type MergeRequest = z.infer<typeof mergeRequestSchema>;

export const jobSchema = z.object({
  id: z.string(),
  type: z.enum(["split", "merge"]),
  status: z.enum(["pending", "processing", "completed", "error"]),
  progress: z.number().min(0).max(100),
  inputVideos: z.array(z.string()),
  outputVideos: z.array(z.string()),
  error: z.string().optional(),
  createdAt: z.number(),
  completedAt: z.number().optional(),
});

export type Job = z.infer<typeof jobSchema>;

export const statsSchema = z.object({
  totalVideosSplit: z.number(),
  totalVideosMerged: z.number(),
  totalSegmentsCreated: z.number(),
  totalTimeSaved: z.number(),
});

export type Stats = z.infer<typeof statsSchema>;

export const users = null;
export const insertUserSchema = z.object({
  username: z.string(),
  password: z.string(),
});
export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = { id: string; username: string; password: string };
