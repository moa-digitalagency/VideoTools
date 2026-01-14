import { useQuery } from "@tanstack/react-query";
import { Scissors, Combine, Layers, Clock, Trophy, Star, Zap, Target } from "lucide-react";
import { StatsCard } from "@/components/StatsCard";
import { AchievementBadge } from "@/components/AchievementBadge";
import type { Stats } from "@/lib/types";

const achievements = [
  {
    id: "first-split",
    title: "First Cut",
    description: "Split your first video",
    icon: Scissors,
    requirement: (stats: Stats) => stats.totalVideosSplit >= 1,
    progress: (stats: Stats) => stats.totalVideosSplit,
    total: 1,
  },
  {
    id: "first-merge",
    title: "Fusion Master",
    description: "Merge your first videos",
    icon: Combine,
    requirement: (stats: Stats) => stats.totalVideosMerged >= 1,
    progress: (stats: Stats) => stats.totalVideosMerged,
    total: 1,
  },
  {
    id: "segment-pro",
    title: "Segment Pro",
    description: "Create 10+ segments",
    icon: Layers,
    requirement: (stats: Stats) => stats.totalSegmentsCreated >= 10,
    progress: (stats: Stats) => stats.totalSegmentsCreated,
    total: 10,
  },
  {
    id: "time-saver",
    title: "Time Saver",
    description: "Process 5 minutes of video",
    icon: Clock,
    requirement: (stats: Stats) => stats.totalTimeSaved >= 300,
    progress: (stats: Stats) => stats.totalTimeSaved,
    total: 300,
  },
  {
    id: "power-user",
    title: "Power User",
    description: "Split 5 videos",
    icon: Zap,
    requirement: (stats: Stats) => stats.totalVideosSplit >= 5,
    progress: (stats: Stats) => stats.totalVideosSplit,
    total: 5,
  },
  {
    id: "merge-master",
    title: "Merge Master",
    description: "Merge 5 projects",
    icon: Target,
    requirement: (stats: Stats) => stats.totalVideosMerged >= 5,
    progress: (stats: Stats) => stats.totalVideosMerged,
    total: 5,
  },
];

function formatTime(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const mins = Math.floor(seconds / 60);
  if (mins < 60) return `${mins}m`;
  const hours = Math.floor(mins / 60);
  return `${hours}h ${mins % 60}m`;
}

export default function StatsPage() {
  const { data: stats, isLoading } = useQuery<Stats>({
    queryKey: ["/api/stats"],
  });

  const defaultStats: Stats = {
    totalVideosSplit: 0,
    totalVideosMerged: 0,
    totalSegmentsCreated: 0,
    totalTimeSaved: 0,
  };

  const currentStats = stats || defaultStats;
  const unlockedCount = achievements.filter((a) => a.requirement(currentStats)).length;

  return (
    <div className="px-4 py-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-1">Your Progress</h2>
        <p className="text-sm text-muted-foreground">
          Track your video processing achievements
        </p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-card rounded-xl border border-card-border p-4 animate-pulse">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-muted rounded-xl" />
                <div className="space-y-2">
                  <div className="h-6 w-12 bg-muted rounded" />
                  <div className="h-4 w-20 bg-muted rounded" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4">
            <StatsCard
              title="Videos Split"
              value={currentStats.totalVideosSplit}
              icon={Scissors}
              color="primary"
            />
            <StatsCard
              title="Videos Merged"
              value={currentStats.totalVideosMerged}
              icon={Combine}
              color="chart-2"
            />
            <StatsCard
              title="Segments Created"
              value={currentStats.totalSegmentsCreated}
              icon={Layers}
              color="chart-4"
            />
            <StatsCard
              title="Time Processed"
              value={formatTime(currentStats.totalTimeSaved)}
              icon={Clock}
              color="chart-5"
            />
          </div>

          <div>
            <div className="flex items-center gap-2 mb-4">
              <Trophy className="w-5 h-5 text-chart-5" />
              <h3 className="text-lg font-medium">Achievements</h3>
              <span className="text-sm text-muted-foreground">
                {unlockedCount}/{achievements.length}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {achievements.map((achievement) => (
                <AchievementBadge
                  key={achievement.id}
                  title={achievement.title}
                  description={achievement.description}
                  icon={achievement.icon}
                  unlocked={achievement.requirement(currentStats)}
                  progress={achievement.progress(currentStats)}
                  total={achievement.total}
                />
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
