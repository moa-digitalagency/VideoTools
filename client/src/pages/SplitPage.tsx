import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Scissors, FileVideo, AlertCircle, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { VideoCard } from "@/components/VideoCard";
import { TimeSelector } from "@/components/TimeSelector";
import { SegmentPreview } from "@/components/SegmentPreview";
import { JobProgress } from "@/components/JobProgress";
import { EmptyState } from "@/components/EmptyState";
import { useToast } from "@/hooks/use-toast";
import { Link } from "wouter";
import type { VideoFile, Job } from "@/lib/types";

export default function SplitPage() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [selectedVideoId, setSelectedVideoId] = useState<string | null>(null);
  const [segmentDuration, setSegmentDuration] = useState(10);

  const { data: videos = [], isLoading: videosLoading } = useQuery<VideoFile[]>({
    queryKey: ["/api/videos"],
  });

  const { data: jobs = [] } = useQuery<Job[]>({
    queryKey: ["/api/jobs"],
    refetchInterval: 2000,
  });

  const splitJobs = jobs.filter((job) => job.type === "split");
  const selectedVideo = videos.find((v) => v.id === selectedVideoId);

  const splitMutation = useMutation({
    mutationFn: async ({ videoId, duration }: { videoId: string; duration: number }) => {
      const response = await fetch("/api/videos/split", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ videoId, segmentDuration: duration }),
      });
      
      if (!response.ok) {
        throw new Error("Split failed");
      }
      
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/jobs"] });
      queryClient.invalidateQueries({ queryKey: ["/api/videos"] });
      queryClient.invalidateQueries({ queryKey: ["/api/stats"] });
      toast({
        title: "Split started!",
        description: "Your video is being split into segments.",
      });
      setSelectedVideoId(null);
    },
    onError: () => {
      toast({
        title: "Split failed",
        description: "Please try again.",
        variant: "destructive",
      });
    },
  });

  const handleSplit = () => {
    if (selectedVideoId) {
      splitMutation.mutate({ videoId: selectedVideoId, duration: segmentDuration });
    }
  };

  const handleDownloadAll = (jobId: string) => {
    window.open(`/api/jobs/${jobId}/download`, "_blank");
  };

  return (
    <div className="px-4 py-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">Split Video</h2>
        <p className="text-sm text-muted-foreground">
          Cut your video into precise segments
        </p>
      </div>

      {splitJobs.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-muted-foreground">Recent Operations</h3>
          {splitJobs.slice(0, 3).map((job) => (
            <JobProgress
              key={job.id}
              job={job}
              onDownload={() => handleDownloadAll(job.id)}
            />
          ))}
        </div>
      )}

      {videosLoading ? (
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-muted rounded-xl" />
          <div className="h-24 bg-muted rounded-xl" />
        </div>
      ) : videos.length === 0 ? (
        <EmptyState
          icon={FileVideo}
          title="No videos to split"
          description="Upload a video first, then come back here to split it."
          action={
            <Link href="/">
              <Button data-testid="button-upload-first">Upload Video</Button>
            </Link>
          }
        />
      ) : (
        <>
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-3">
              Select a video to split
            </h3>
            <div className="space-y-3">
              {videos.map((video) => (
                <VideoCard
                  key={video.id}
                  video={video}
                  onSelect={setSelectedVideoId}
                  selected={selectedVideoId === video.id}
                />
              ))}
            </div>
          </div>

          {selectedVideo && (
            <div className="bg-card rounded-xl border border-card-border p-6 space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-1">Segment Duration</h3>
                <p className="text-sm text-muted-foreground">
                  Each segment will be exactly this length
                </p>
              </div>

              <TimeSelector
                value={segmentDuration}
                onChange={setSegmentDuration}
              />

              {selectedVideo.duration && (
                <SegmentPreview
                  totalDuration={selectedVideo.duration}
                  segmentDuration={segmentDuration}
                />
              )}

              {!selectedVideo.duration && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground bg-muted/50 rounded-lg p-3">
                  <AlertCircle className="w-4 h-4" />
                  <span>Video duration will be calculated during processing</span>
                </div>
              )}

              <Button
                className="w-full h-12 rounded-xl text-base"
                onClick={handleSplit}
                disabled={splitMutation.isPending}
                data-testid="button-split"
              >
                {splitMutation.isPending ? (
                  <>Processing...</>
                ) : (
                  <>
                    <Scissors className="w-5 h-5 mr-2" />
                    Split Video
                  </>
                )}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
