import { LucideIcon, Lock } from "lucide-react";

interface AchievementBadgeProps {
  title: string;
  description: string;
  icon: LucideIcon;
  unlocked: boolean;
  progress?: number;
  total?: number;
}

export function AchievementBadge({ 
  title, 
  description, 
  icon: Icon, 
  unlocked,
  progress,
  total,
}: AchievementBadgeProps) {
  return (
    <div 
      className={`relative bg-card rounded-xl border p-4 text-center transition-all ${
        unlocked 
          ? "border-primary shadow-lg" 
          : "border-card-border opacity-75"
      }`}
    >
      <div 
        className={`w-14 h-14 mx-auto rounded-full flex items-center justify-center mb-3 ${
          unlocked 
            ? "bg-gradient-to-br from-primary to-chart-5 text-white" 
            : "bg-muted text-muted-foreground"
        }`}
      >
        {unlocked ? (
          <Icon className="w-7 h-7" />
        ) : (
          <Lock className="w-6 h-6" />
        )}
      </div>
      
      <h4 className="font-semibold text-sm">{title}</h4>
      <p className="text-xs text-muted-foreground mt-1">{description}</p>
      
      {!unlocked && progress !== undefined && total !== undefined && (
        <div className="mt-3">
          <div className="h-1.5 bg-muted rounded-full overflow-hidden">
            <div 
              className="h-full bg-primary transition-all"
              style={{ width: `${Math.min((progress / total) * 100, 100)}%` }}
            />
          </div>
          <p className="text-xs text-muted-foreground mt-1">{progress}/{total}</p>
        </div>
      )}
      
      {unlocked && (
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-chart-4 rounded-full flex items-center justify-center">
          <span className="text-white text-xs">✓</span>
        </div>
      )}
    </div>
  );
}
