import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import time


class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class JobType(Enum):
    SPLIT = "split"
    MERGE = "merge"


@dataclass
class Job:
    id: str
    type: JobType
    status: JobStatus
    progress: int = 0
    created_at: float = field(default_factory=time.time)
    video_id: Optional[str] = None
    video_ids: Optional[List[str]] = None
    segment_duration: Optional[int] = None
    outputs: Optional[List[str]] = None
    output: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        result = {
            "id": self.id,
            "type": self.type.value,
            "status": self.status.value,
            "progress": self.progress,
            "createdAt": int(self.created_at * 1000),
        }
        if self.outputs:
            result["outputs"] = self.outputs
        if self.output:
            result["output"] = self.output
        if self.error:
            result["error"] = self.error
        return result
    
    @staticmethod
    def create_split_job(video_id: str, segment_duration: int) -> 'Job':
        return Job(
            id=str(uuid.uuid4()),
            type=JobType.SPLIT,
            status=JobStatus.PENDING,
            video_id=video_id,
            segment_duration=segment_duration,
        )
    
    @staticmethod
    def create_merge_job(video_ids: List[str]) -> 'Job':
        return Job(
            id=str(uuid.uuid4()),
            type=JobType.MERGE,
            status=JobStatus.PENDING,
            video_ids=video_ids,
        )


jobs_store: Dict[str, Job] = {}
