import uuid
import threading
from typing import Dict, Any


_JOBS: Dict[str, Dict[str, Any]] = {}
_LOCK = threading.Lock()


def create_job() -> str:
    job_id = uuid.uuid4().hex
    with _LOCK:
        _JOBS[job_id] = {"status": "queued", "progress": 0, "result": None, "error": None}
    return job_id


def set_status(job_id: str, status: str, progress: int = None):
    with _LOCK:
        if job_id in _JOBS:
            _JOBS[job_id]["status"] = status
            if progress is not None:
                _JOBS[job_id]["progress"] = progress


def set_result(job_id: str, result: Dict[str, Any]):
    with _LOCK:
        if job_id in _JOBS:
            _JOBS[job_id]["result"] = result
            _JOBS[job_id]["status"] = "done"
            _JOBS[job_id]["progress"] = 100


def set_error(job_id: str, error_message: str):
    with _LOCK:
        if job_id in _JOBS:
            _JOBS[job_id]["error"] = error_message
            _JOBS[job_id]["status"] = "error"


def get_job(job_id: str) -> Dict[str, Any]:
    with _LOCK:
        return _JOBS.get(job_id, {"status": "not_found"})


