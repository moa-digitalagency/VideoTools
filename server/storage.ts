import { randomUUID } from "crypto";

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

export interface IStorage {
  getVideos(): Promise<VideoFile[]>;
  getVideo(id: string): Promise<VideoFile | undefined>;
  addVideo(video: Omit<VideoFile, "id" | "createdAt">): Promise<VideoFile>;
  updateVideo(id: string, updates: Partial<VideoFile>): Promise<VideoFile | undefined>;
  deleteVideo(id: string): Promise<boolean>;
  
  getJobs(): Promise<Job[]>;
  getJob(id: string): Promise<Job | undefined>;
  addJob(job: Omit<Job, "id" | "createdAt">): Promise<Job>;
  updateJob(id: string, updates: Partial<Job>): Promise<Job | undefined>;
  
  getStats(): Promise<Stats>;
  updateStats(updates: Partial<Stats>): Promise<Stats>;
}

export class MemStorage implements IStorage {
  private videos: Map<string, VideoFile>;
  private jobs: Map<string, Job>;
  private stats: Stats;

  constructor() {
    this.videos = new Map();
    this.jobs = new Map();
    this.stats = {
      totalVideosSplit: 0,
      totalVideosMerged: 0,
      totalSegmentsCreated: 0,
      totalTimeSaved: 0,
    };
  }

  async getVideos(): Promise<VideoFile[]> {
    return Array.from(this.videos.values()).sort((a, b) => b.createdAt - a.createdAt);
  }

  async getVideo(id: string): Promise<VideoFile | undefined> {
    return this.videos.get(id);
  }

  async addVideo(video: Omit<VideoFile, "id" | "createdAt">): Promise<VideoFile> {
    const id = randomUUID();
    const newVideo: VideoFile = {
      ...video,
      id,
      createdAt: Date.now(),
    };
    this.videos.set(id, newVideo);
    return newVideo;
  }

  async updateVideo(id: string, updates: Partial<VideoFile>): Promise<VideoFile | undefined> {
    const video = this.videos.get(id);
    if (!video) return undefined;
    const updated = { ...video, ...updates };
    this.videos.set(id, updated);
    return updated;
  }

  async deleteVideo(id: string): Promise<boolean> {
    return this.videos.delete(id);
  }

  async getJobs(): Promise<Job[]> {
    return Array.from(this.jobs.values()).sort((a, b) => b.createdAt - a.createdAt);
  }

  async getJob(id: string): Promise<Job | undefined> {
    return this.jobs.get(id);
  }

  async addJob(job: Omit<Job, "id" | "createdAt">): Promise<Job> {
    const id = randomUUID();
    const newJob: Job = {
      ...job,
      id,
      createdAt: Date.now(),
    };
    this.jobs.set(id, newJob);
    return newJob;
  }

  async updateJob(id: string, updates: Partial<Job>): Promise<Job | undefined> {
    const job = this.jobs.get(id);
    if (!job) return undefined;
    const updated = { ...job, ...updates };
    this.jobs.set(id, updated);
    return updated;
  }

  async getStats(): Promise<Stats> {
    return { ...this.stats };
  }

  async updateStats(updates: Partial<Stats>): Promise<Stats> {
    this.stats = { ...this.stats, ...updates };
    return { ...this.stats };
  }
}

export const storage = new MemStorage();
