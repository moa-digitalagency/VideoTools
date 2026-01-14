import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Combine, FileVideo, ArrowUp, ArrowDown, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { VideoCard } from "@/components/VideoCard";
import { JobProgress } from "@/components/JobProgress";
import { EmptyState } from "@/components/EmptyState";
import { useToast } from "@/hooks/use-toast";
import { Link } from "wouter";
import type { VideoFile, Job } from "@/lib/types";

export default function MergePage() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [selectedVideoIds, setSelectedVideoIds] = useState<string[]>([]);

  const { data: videos = [], isLoading: videosLoading } = useQuery<VideoFile[]>({
    queryKey: ["/api/videos"],
  });

  const { data: jobs = [] } = useQuery<Job[]>({
    queryKey: ["/api/jobs"],
    refetchInterval: 2000,
  });

  const mergeJobs = jobs.filter((job) => job.type === "merge");

  const mergeMutation = useMutation({
    mutationFn: async (videoIds: string[]) => {
      const response = await fetch("/api/videos/merge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ videoIds }),
      });
      
      if (!response.ok) {
        throw new Error("Merge failed");
      }
      
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/jobs"] });
      queryClient.invalidateQueries({ queryKey: ["/api/videos"] });
      queryClient.invalidateQueries({ queryKey: ["/api/stats"] });
      toast({
        title: "Merge started!",
        description: "Your videos are being merged into one.",
      });
      setSelectedVideoIds([]);
    },
    onError: () => {
      toast({
        title: "Merge failed",
        description: "Please try again.",
        variant: "destructive",
      });
    },
  });

  const toggleVideoSelection = (id: string) => {
    setSelectedVideoIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((v) => v !== id);
      }
      return [...prev, id];
    });
  };

  const moveVideo = (index: number, direction: "up" | "down") => {
    const newOrder = [...selectedVideoIds];
    const newIndex = direction === "up" ? index - 1 : index + 1;
    if (newIndex >= 0 && newIndex < newOrder.length) {
      [newOrder[index], newOrder[newIndex]] = [newOrder[newIndex], newOrder[index]];
      setSelectedVideoIds(newOrder);
    }
  };

  const removeFromSelection = (id: string) => {
    setSelectedVideoIds((prev) => prev.filter((v) => v !== id));
  };

  const handleMerge = () => {
    if (selectedVideoIds.length >= 2) {
      mergeMutation.mutate(selectedVideoIds);
    }
  };

  const handleDownload = (jobId: string) => {
    window.open(`/api/jobs/${jobId}/download`, "_blank");
  };

  const selectedVideos = selectedVideoIds
    .map((id) => videos.find((v) => v.id === id))
    .filter(Boolean) as VideoFile[];

  const availableVideos = videos.filter((v) => !selectedVideoIds.includes(v.id));

  return (
    <div className="px-4 py-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">Merge Videos</h2>
        <p className="text-sm text-muted-foreground">
          Combine multiple videos into one seamless file
        </p>
      </div>

      {mergeJobs.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-muted-foreground">Recent Operations</h3>
          {mergeJobs.slice(0, 3).map((job) => (
            <JobProgress
              key={job.id}
              job={job}
              onDownload={() => handleDownload(job.id)}
            />
          ))}
        </div>
      )}

      {videosLoading ? (
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-muted rounded-xl" />
          <div className="h-24 bg-muted rounded-xl" />
        </div>
      ) : videos.length < 2 ? (
        <EmptyState
          icon={FileVideo}
          title="Not enough videos"
          description="You need at least 2 videos to merge. Upload more videos first."
          action={
            <Link href="/">
              <Button data-testid="button-upload-more">Upload Videos</Button>
            </Link>
          }
        />
      ) : (
        <>
          {selectedVideoIds.length > 0 && (
            <div className="bg-card rounded-xl border border-card-border p-4 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Merge Order</h3>
                <span className="text-sm text-muted-foreground">
                  {selectedVideoIds.length} selected
                </span>
              </div>

              <div className="space-y-2" data-testid="list-merge-order">
                {selectedVideos.map((video, index) => (
                  <div
                    key={video.id}
                    className="flex items-center gap-3 bg-muted/50 rounded-lg p-3"
                    data-testid={`item-merge-video-${video.id}`}
                  >
                    <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold flex-shrink-0">
                      {index + 1}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{video.originalName}</p>
                    </div>

                    <div className="flex items-center gap-1" data-testid={`controls-reorder-${video.id}`}>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => moveVideo(index, "up")}
                        disabled={index === 0}
                        className="h-8 w-8"
                        data-testid={`button-move-up-${video.id}`}
                      >
                        <ArrowUp className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => moveVideo(index, "down")}
                        disabled={index === selectedVideoIds.length - 1}
                        className="h-8 w-8"
                        data-testid={`button-move-down-${video.id}`}
                      >
                        <ArrowDown className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeFromSelection(video.id)}
                        className="h-8 w-8 text-destructive"
                        data-testid={`button-remove-${video.id}`}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>

              <Button
                className="w-full h-12 rounded-xl text-base"
                onClick={handleMerge}
                disabled={selectedVideoIds.length < 2 || mergeMutation.isPending}
                data-testid="button-merge"
              >
                {mergeMutation.isPending ? (
                  <>Processing...</>
                ) : (
                  <>
                    <Combine className="w-5 h-5 mr-2" />
                    Merge {selectedVideoIds.length} Videos
                  </>
                )}
              </Button>
            </div>
          )}

          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-3">
              {selectedVideoIds.length > 0 ? "Add more videos" : "Select videos to merge"}
            </h3>
            <div className="space-y-3">
              {availableVideos.map((video) => (
                <VideoCard
                  key={video.id}
                  video={video}
                  onSelect={toggleVideoSelection}
                  selected={false}
                />
              ))}
            </div>

            {availableVideos.length === 0 && selectedVideoIds.length > 0 && (
              <p className="text-sm text-muted-foreground text-center py-4">
                All videos are selected
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
