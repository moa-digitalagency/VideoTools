import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional
import time


@dataclass
class Video:
    id: str
    filename: str
    original_name: str
    size: int
    duration: float
    path: str
    created_at: float = field(default_factory=time.time)
    codec: Optional[str] = None
    resolution: Optional[str] = None
    bitrate: Optional[int] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "filename": self.filename,
            "originalName": self.original_name,
            "size": self.size,
            "duration": self.duration,
            "path": self.path,
            "createdAt": int(self.created_at * 1000),
            "codec": self.codec,
            "resolution": self.resolution,
            "bitrate": self.bitrate,
        }
    
    @staticmethod
    def create(filename: str, original_name: str, size: int, duration: float, 
               path: str, codec: Optional[str] = None, resolution: Optional[str] = None, 
               bitrate: Optional[int] = None) -> 'Video':
        return Video(
            id=str(uuid.uuid4()),
            filename=filename,
            original_name=original_name,
            size=size,
            duration=duration,
            path=path,
            codec=codec,
            resolution=resolution,
            bitrate=bitrate,
        )


videos_store: Dict[str, Video] = {}
