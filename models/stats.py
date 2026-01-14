from dataclasses import dataclass


@dataclass
class Stats:
    total_videos_split: int = 0
    total_videos_merged: int = 0
    total_segments_created: int = 0
    total_time_saved: float = 0
    
    def to_dict(self) -> dict:
        return {
            "totalVideosSplit": self.total_videos_split,
            "totalVideosMerged": self.total_videos_merged,
            "totalSegmentsCreated": self.total_segments_created,
            "totalTimeSaved": self.total_time_saved,
        }
    
    def add_split(self, segment_count: int, duration: float):
        self.total_videos_split += 1
        self.total_segments_created += segment_count
        self.total_time_saved += duration
    
    def add_merge(self, duration: float):
        self.total_videos_merged += 1
        self.total_time_saved += duration


stats_store = Stats()
