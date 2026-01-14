import { Loader2, CheckCircle2, XCircle, Download, Scissors, Combine } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import type { Job } from "@/lib/types";

interface JobProgressProps {
  job: Job;
  onDownload?: () => void;
  onRetry?: () => void;
}

export function JobProgress({ job, onDownload, onRetry }: JobProgressProps) {
  const Icon = job.type === "split" ? Scissors : Combine;
  const label = job.type === "split" ? "Splitting" : "Merging";
  
  return (
    <div 
      className="bg-card rounded-xl border border-card-border p-4"
      data-testid={`job-${job.id}`}
    >
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
          job.status === "completed" 
            ? "bg-chart-4/20" 
            : job.status === "error"
            ? "bg-destructive/20"
            : "bg-primary/20"
        }`}>
          {job.status === "processing" ? (
            <Loader2 className="w-5 h-5 text-primary animate-spin" />
          ) : job.status === "completed" ? (
            <CheckCircle2 className="w-5 h-5 text-chart-4" />
          ) : job.status === "error" ? (
            <XCircle className="w-5 h-5 text-destructive" />
          ) : (
            <Icon className="w-5 h-5 text-primary" />
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm">
            {job.status === "completed" 
              ? `${label} complete!` 
              : job.status === "error"
              ? `${label} failed`
              : job.status === "processing"
              ? `${label} video...`
              : `${label} pending`
            }
          </p>
          <p className="text-xs text-muted-foreground">
            {job.status === "completed" && job.outputVideos.length > 0
              ? `${job.outputVideos.length} file${job.outputVideos.length !== 1 ? "s" : ""} ready`
              : job.status === "error"
              ? job.error || "An error occurred"
              : `${job.progress}% complete`
            }
          </p>
        </div>
        
        {job.status === "completed" && onDownload && (
          <Button 
            size="sm" 
            onClick={onDownload}
            data-testid={`button-download-job-${job.id}`}
          >
            <Download className="w-4 h-4 mr-1" />
            Download
          </Button>
        )}
        
        {job.status === "error" && onRetry && (
          <Button 
            variant="outline" 
            size="sm" 
            onClick={onRetry}
            data-testid={`button-retry-job-${job.id}`}
          >
            Retry
          </Button>
        )}
      </div>
      
      {(job.status === "processing" || job.status === "pending") && (
        <Progress value={job.progress} className="h-2" />
      )}
    </div>
  );
}
