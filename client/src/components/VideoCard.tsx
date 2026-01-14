import { FileVideo, Trash2, Play, Download, Clock, GripVertical } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { VideoFile } from "@/lib/types";

interface VideoCardProps {
  video: VideoFile;
  onDelete?: (id: string) => void;
  onPreview?: (id: string) => void;
  onDownload?: (id: string) => void;
  onSelect?: (id: string) => void;
  selected?: boolean;
  showDragHandle?: boolean;
  orderNumber?: number;
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function VideoCard({
  video,
  onDelete,
  onPreview,
  onDownload,
  onSelect,
  selected = false,
  showDragHandle = false,
  orderNumber,
}: VideoCardProps) {
  return (
    <div
      className={`relative bg-card rounded-xl border transition-all ${
        selected ? "border-primary ring-2 ring-primary/20" : "border-card-border"
      }`}
      data-testid={`card-video-${video.id}`}
    >
      {orderNumber !== undefined && (
        <div className="absolute -left-3 -top-3 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold z-10">
          {orderNumber}
        </div>
      )}
      
      <div className="p-4 flex gap-4">
        {showDragHandle && (
          <div className="flex items-center cursor-grab active:cursor-grabbing">
            <GripVertical className="w-5 h-5 text-muted-foreground" />
          </div>
        )}
        
        <div 
          className="aspect-video w-24 sm:w-32 rounded-lg bg-muted flex items-center justify-center flex-shrink-0 relative overflow-hidden group cursor-pointer hover-elevate"
          onClick={() => onPreview?.(video.id)}
        >
          <FileVideo className="w-8 h-8 text-muted-foreground" />
          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <Play className="w-8 h-8 text-white" fill="white" />
          </div>
          {video.duration && (
            <Badge 
              variant="secondary" 
              className="absolute bottom-1 right-1 text-xs px-1.5 py-0.5"
            >
              <Clock className="w-3 h-3 mr-1" />
              {formatDuration(video.duration)}
            </Badge>
          )}
        </div>
        
        <div className="flex-1 min-w-0 flex flex-col justify-between">
          <div>
            <p className="font-medium text-sm truncate" title={video.originalName}>
              {video.originalName}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {formatSize(video.size)}
            </p>
          </div>
          
          <div className="flex gap-2 mt-3 flex-wrap">
            {onSelect && (
              <Button
                variant={selected ? "default" : "outline"}
                size="sm"
                onClick={() => onSelect(video.id)}
                data-testid={`button-select-${video.id}`}
              >
                {selected ? "Selected" : "Select"}
              </Button>
            )}
            {onDownload && (
              <Button
                variant="outline"
                size="icon"
                onClick={() => onDownload(video.id)}
                data-testid={`button-download-${video.id}`}
              >
                <Download className="w-4 h-4" />
              </Button>
            )}
            {onDelete && (
              <Button
                variant="outline"
                size="icon"
                onClick={() => onDelete(video.id)}
                className="text-destructive hover:text-destructive"
                data-testid={`button-delete-${video.id}`}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
