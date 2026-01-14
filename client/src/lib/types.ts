export interface VideoFile {
  id: string;
  filename: string;
  originalName: string;
  size: number;
  duration?: number;
  path: string;
  createdAt: number;
}

export interface Job {
  id: string;
  type: "split" | "merge";
  status: "pending" | "processing" | "completed" | "error";
  progress: number;
  inputVideos: string[];
  outputVideos: string[];
  error?: string;
  createdAt: number;
  completedAt?: number;
}

export interface Stats {
  totalVideosSplit: number;
  totalVideosMerged: number;
  totalSegmentsCreated: number;
  totalTimeSaved: number;
}
