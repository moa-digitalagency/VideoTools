import { useCallback, useState } from "react";
import { Upload, FileVideo, X, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface UploadZoneProps {
  onUpload: (file: File) => Promise<void>;
  accept?: string;
  maxSize?: number;
}

export function UploadZone({ 
  onUpload, 
  accept = "video/*",
  maxSize = 500 * 1024 * 1024 
}: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(async (file: File) => {
    setError(null);
    
    if (!file.type.startsWith("video/")) {
      setError("Please upload a video file");
      return;
    }
    
    if (file.size > maxSize) {
      setError(`File too large. Maximum size is ${Math.round(maxSize / 1024 / 1024)}MB`);
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + 10;
      });
    }, 200);

    try {
      await onUpload(file);
      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadedFile(file.name);
      setTimeout(() => {
        setUploadedFile(null);
        setUploadProgress(0);
      }, 2000);
    } catch (err) {
      clearInterval(progressInterval);
      setError("Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  }, [onUpload, maxSize]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFile(file);
    }
  }, [handleFile]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  }, [handleFile]);

  return (
    <div className="w-full">
      <div
        className={`relative min-h-48 border-2 border-dashed rounded-xl flex flex-col items-center justify-center gap-4 p-6 transition-all cursor-pointer ${
          isDragging
            ? "border-primary bg-accent scale-[1.02]"
            : uploadedFile
            ? "border-chart-4 bg-chart-4/10"
            : error
            ? "border-destructive bg-destructive/10"
            : "border-muted hover:border-primary hover:bg-accent/50"
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => document.getElementById("file-input")?.click()}
        data-testid="zone-upload-drop"
      >
        <input
          id="file-input"
          type="file"
          accept={accept}
          onChange={handleInputChange}
          className="hidden"
          data-testid="input-file"
        />

        {isUploading ? (
          <div className="flex flex-col items-center gap-4 w-full max-w-xs">
            <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center animate-pulse">
              <FileVideo className="w-8 h-8 text-primary" />
            </div>
            <p className="text-sm font-medium">Uploading...</p>
            <Progress value={uploadProgress} className="h-2" />
            <span className="text-xs text-muted-foreground">{uploadProgress}%</span>
          </div>
        ) : uploadedFile ? (
          <div className="flex flex-col items-center gap-3">
            <div className="w-16 h-16 rounded-full bg-chart-4/20 flex items-center justify-center">
              <CheckCircle2 className="w-8 h-8 text-chart-4" />
            </div>
            <p className="text-sm font-medium text-chart-4">Upload complete!</p>
            <p className="text-xs text-muted-foreground truncate max-w-[200px]">
              {uploadedFile}
            </p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center gap-3">
            <div className="w-16 h-16 rounded-full bg-destructive/20 flex items-center justify-center">
              <X className="w-8 h-8 text-destructive" />
            </div>
            <p className="text-sm font-medium text-destructive">{error}</p>
            <Button variant="outline" size="sm" onClick={(e) => {
              e.stopPropagation();
              setError(null);
            }}>
              Try again
            </Button>
          </div>
        ) : (
          <>
            <div className="w-16 h-16 rounded-full bg-accent flex items-center justify-center">
              <Upload className="w-8 h-8 text-primary" />
            </div>
            <div className="text-center">
              <p className="text-base font-medium">Drop your video here</p>
              <p className="text-sm text-muted-foreground mt-1">or tap to browse</p>
            </div>
            <Button className="w-full max-w-xs rounded-xl h-12" data-testid="button-browse">
              <FileVideo className="w-5 h-5 mr-2" />
              Choose Video
            </Button>
            <p className="text-xs text-muted-foreground">
              MP4, MOV, AVI up to {Math.round(maxSize / 1024 / 1024)}MB
            </p>
          </>
        )}
      </div>
    </div>
  );
}
