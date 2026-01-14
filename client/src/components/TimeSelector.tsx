import { Minus, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface TimeSelectorProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  presets?: number[];
}

const defaultPresets = [5, 10, 30, 60];

export function TimeSelector({
  value,
  onChange,
  min = 1,
  max = 3600,
  presets = defaultPresets,
}: TimeSelectorProps) {
  const increment = () => {
    if (value < max) {
      onChange(Math.min(value + 1, max));
    }
  };

  const decrement = () => {
    if (value > min) {
      onChange(Math.max(value - 1, min));
    }
  };

  const formatTime = (seconds: number): string => {
    if (seconds >= 60) {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return secs > 0 ? `${mins}m ${secs}s` : `${mins}m`;
    }
    return `${seconds}s`;
  };

  return (
    <div className="flex flex-col items-center gap-6">
      <div className="flex items-center gap-4">
        <Button
          variant="outline"
          size="icon"
          className="w-14 h-14 rounded-xl"
          onClick={decrement}
          disabled={value <= min}
          data-testid="button-decrement"
        >
          <Minus className="w-6 h-6" />
        </Button>
        
        <div className="w-32 text-center">
          <span className="text-4xl font-bold text-primary" data-testid="text-time-value">
            {value}
          </span>
          <p className="text-sm text-muted-foreground mt-1">seconds</p>
        </div>
        
        <Button
          variant="outline"
          size="icon"
          className="w-14 h-14 rounded-xl"
          onClick={increment}
          disabled={value >= max}
          data-testid="button-increment"
        >
          <Plus className="w-6 h-6" />
        </Button>
      </div>
      
      <div className="flex gap-2 flex-wrap justify-center">
        {presets.map((preset) => (
          <Button
            key={preset}
            variant={value === preset ? "default" : "secondary"}
            size="sm"
            className="rounded-full px-4"
            onClick={() => onChange(preset)}
            data-testid={`button-preset-${preset}`}
          >
            {formatTime(preset)}
          </Button>
        ))}
      </div>
    </div>
  );
}
