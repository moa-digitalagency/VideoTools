import { LucideIcon } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: number | string;
  icon: LucideIcon;
  color: "primary" | "chart-2" | "chart-3" | "chart-4" | "chart-5";
}

const colorClasses = {
  primary: "bg-primary/20 text-primary",
  "chart-2": "bg-chart-2/20 text-chart-2",
  "chart-3": "bg-chart-3/20 text-chart-3",
  "chart-4": "bg-chart-4/20 text-chart-4",
  "chart-5": "bg-chart-5/20 text-chart-5",
};

export function StatsCard({ title, value, icon: Icon, color }: StatsCardProps) {
  return (
    <div className="bg-card rounded-xl border border-card-border p-4">
      <div className="flex items-center gap-3">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <p className="text-2xl font-bold" data-testid={`stat-value-${title.toLowerCase().replace(/\s/g, "-")}`}>
            {value}
          </p>
          <p className="text-sm text-muted-foreground">{title}</p>
        </div>
      </div>
    </div>
  );
}
