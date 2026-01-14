import { Link, useLocation } from "wouter";
import { Upload, Scissors, Combine, Trophy } from "lucide-react";

const navItems = [
  { path: "/", label: "Upload", icon: Upload },
  { path: "/split", label: "Split", icon: Scissors },
  { path: "/merge", label: "Merge", icon: Combine },
  { path: "/stats", label: "Stats", icon: Trophy },
];

export function BottomNav() {
  const [location] = useLocation();

  return (
    <nav 
      className="fixed bottom-0 left-0 right-0 bg-card border-t border-card-border h-16 flex items-center justify-around px-4 z-50 safe-area-pb"
      data-testid="nav-bottom"
    >
      {navItems.map((item) => {
        const isActive = location === item.path;
        const Icon = item.icon;
        return (
          <Link key={item.path} href={item.path}>
            <button
              className={`flex flex-col items-center justify-center gap-1 px-4 py-2 rounded-xl transition-all min-w-[64px] ${
                isActive 
                  ? "text-primary bg-accent" 
                  : "text-muted-foreground"
              }`}
              data-testid={`nav-${item.label.toLowerCase()}`}
            >
              <div className="relative">
                {isActive && (
                  <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-6 h-1 bg-primary rounded-full" />
                )}
                <Icon className="w-6 h-6" />
              </div>
              <span className="text-xs font-medium">{item.label}</span>
            </button>
          </Link>
        );
      })}
    </nav>
  );
}
