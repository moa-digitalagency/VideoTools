import { Scissors } from "lucide-react";

interface SegmentPreviewProps {
  totalDuration: number;
  segmentDuration: number;
}

export function SegmentPreview({ totalDuration, segmentDuration }: SegmentPreviewProps) {
  const segmentCount = Math.ceil(totalDuration / segmentDuration);
  const lastSegmentDuration = totalDuration % segmentDuration || segmentDuration;
  
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const displaySegments = Math.min(segmentCount, 6);
  const hasMore = segmentCount > 6;

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-muted-foreground">Preview</h3>
        <div className="flex items-center gap-2 text-sm">
          <Scissors className="w-4 h-4 text-primary" />
          <span className="font-semibold text-primary" data-testid="text-segment-count">
            {segmentCount} segment{segmentCount !== 1 ? "s" : ""}
          </span>
        </div>
      </div>
      
      <div className="relative h-12 bg-muted rounded-lg overflow-hidden">
        <div className="absolute inset-0 flex">
          {Array.from({ length: displaySegments }).map((_, index) => {
            const isLast = index === segmentCount - 1;
            const duration = isLast ? lastSegmentDuration : segmentDuration;
            const widthPercent = (duration / totalDuration) * 100;
            
            const colors = [
              "bg-primary",
              "bg-chart-2",
              "bg-chart-3",
              "bg-chart-4",
              "bg-chart-5",
              "bg-chart-1",
            ];
            
            return (
              <div
                key={index}
                className={`h-full flex items-center justify-center text-xs font-medium text-white relative ${colors[index % colors.length]}`}
                style={{ width: hasMore && index === displaySegments - 1 ? "auto" : `${widthPercent}%`, flex: hasMore && index === displaySegments - 1 ? 1 : "none" }}
              >
                {hasMore && index === displaySegments - 1 ? (
                  <span className="px-2">+{segmentCount - displaySegments + 1} more</span>
                ) : (
                  <span className="px-1 truncate">{formatTime(duration)}</span>
                )}
                {index < displaySegments - 1 && (
                  <div className="absolute right-0 top-0 bottom-0 w-0.5 bg-background" />
                )}
              </div>
            );
          })}
        </div>
      </div>
      
      <div className="flex justify-between mt-2 text-xs text-muted-foreground">
        <span>0:00</span>
        <span>{formatTime(totalDuration)}</span>
      </div>
    </div>
  );
}
