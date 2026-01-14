import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileVideo, Trash2 } from "lucide-react";
import { UploadZone } from "@/components/UploadZone";
import { VideoCard } from "@/components/VideoCard";
import { EmptyState } from "@/components/EmptyState";
import { useToast } from "@/hooks/use-toast";
import type { VideoFile } from "@/lib/types";

export default function UploadPage() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: videos = [], isLoading } = useQuery<VideoFile[]>({
    queryKey: ["/api/videos"],
  });

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("video", file);
      
      const response = await fetch("/api/videos/upload", {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error("Upload failed");
      }
      
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/videos"] });
      toast({
        title: "Video uploaded!",
        description: "Your video is ready to be processed.",
      });
    },
    onError: () => {
      toast({
        title: "Upload failed",
        description: "Please try again.",
        variant: "destructive",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`/api/videos/${id}`, {
        method: "DELETE",
      });
      
      if (!response.ok) {
        throw new Error("Delete failed");
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/videos"] });
      toast({
        title: "Video deleted",
        description: "The video has been removed.",
      });
    },
  });

  const handleUpload = async (file: File) => {
    await uploadMutation.mutateAsync(file);
  };

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id);
  };

  const handleDownload = (id: string) => {
    window.open(`/api/videos/${id}/download`, "_blank");
  };

  return (
    <div className="px-4 py-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">Upload Video</h2>
        <p className="text-sm text-muted-foreground">
          Add videos to split or merge
        </p>
      </div>

      <UploadZone onUpload={handleUpload} />

      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium">Your Videos</h3>
          <span className="text-sm text-muted-foreground">
            {videos.length} video{videos.length !== 1 ? "s" : ""}
          </span>
        </div>

        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-card rounded-xl border border-card-border p-4 animate-pulse">
                <div className="flex gap-4">
                  <div className="w-24 sm:w-32 aspect-video bg-muted rounded-lg" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-muted rounded w-3/4" />
                    <div className="h-3 bg-muted rounded w-1/4" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : videos.length === 0 ? (
          <EmptyState
            icon={FileVideo}
            title="No videos yet"
            description="Upload your first video to get started with splitting or merging."
          />
        ) : (
          <div className="space-y-3">
            {videos.map((video) => (
              <VideoCard
                key={video.id}
                video={video}
                onDelete={handleDelete}
                onDownload={handleDownload}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
