import logging
from datetime import datetime
from typing import Dict, Any, Optional
import time
from contextlib import contextmanager
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Observability:
    def __init__(self):
        self.metrics = {}
    
    def log_info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log an info message with optional extra context."""
        if extra:
            logger.info(f"{message} | Context: {json.dumps(extra)}")
        else:
            logger.info(message)
    
    def log_error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """Log an error message with optional extra context and exception info."""
        if extra:
            logger.error(f"{message} | Context: {json.dumps(extra)}", exc_info=exc_info)
        else:
            logger.error(message, exc_info=exc_info)
    
    def log_warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log a warning message with optional extra context."""
        if extra:
            logger.warning(f"{message} | Context: {json.dumps(extra)}")
        else:
            logger.warning(message)
    
    def log_debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log a debug message with optional extra context."""
        if extra:
            logger.debug(f"{message} | Context: {json.dumps(extra)}")
        else:
            logger.debug(message)
    
    def start_timer(self) -> float:
        """Start a timer and return the start time."""
        return time.time()
    
    def stop_timer(self, start_time: float) -> float:
        """Calculate elapsed time since start_time."""
        return time.time() - start_time
    
    @contextmanager
    def timed_execution(self, operation_name: str):
        """Context manager to time the execution of a block of code."""
        start_time = self.start_timer()
        try:
            yield
        finally:
            elapsed_time = self.stop_timer(start_time)
            self.log_info(f"Operation '{operation_name}' completed", {"duration_seconds": elapsed_time})
            
            # Track performance metric
            self.add_metric(operation_name, elapsed_time)
    
    def add_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Add a metric value with optional tags."""
        metric_key = f"{name}:{json.dumps(tags) if tags else ''}"
        if metric_key not in self.metrics:
            self.metrics[metric_key] = []
        self.metrics[metric_key].append({
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "tags": tags
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return self.metrics.copy()
    
    def track_response_quality(self, query: str, response: str, context_used: list, score: float) -> bool:
        """
        Track the quality of a response based on various factors.
        
        Args:
            query: The original query
            response: The generated response
            context_used: Context that was used to generate the response
            score: Quality score (0.0 to 1.0)
            
        Returns:
            True if tracking was successful
        """
        quality_data = {
            "query_length": len(query),
            "response_length": len(response),
            "context_count": len(context_used),
            "quality_score": score,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            self.log_info("Response quality tracked", quality_data)
            self.add_metric("response_quality", score, {"type": "overall"})
            return True
        except Exception as e:
            self.log_error(f"Failed to track response quality: {str(e)}")
            return False


# Global instance
observability = Observability()


def get_observability() -> Observability:
    """Get the global observability instance."""
    return observability