"""
Metrics and observability utilities.

Provides performance tracking, token counting, and metrics collection.
"""

import time
import functools
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class OperationMetrics:
    """Metrics for a single operation."""

    operation_name: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def complete(self, success: bool = True, error_message: Optional[str] = None) -> None:
        """Mark operation as complete."""
        self.end_time = datetime.now()
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        self.success = success
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation": self.operation_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class MetricsCollector:
    """Collects and aggregates metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.operations: list[OperationMetrics] = []
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}

    def start_operation(self, name: str, **metadata) -> OperationMetrics:
        """
        Start tracking an operation.

        Args:
            name: Operation name
            **metadata: Additional metadata

        Returns:
            OperationMetrics instance
        """
        metric = OperationMetrics(operation_name=name, metadata=metadata)
        self.operations.append(metric)
        return metric

    def increment_counter(self, name: str, value: int = 1) -> None:
        """
        Increment a counter.

        Args:
            name: Counter name
            value: Value to increment by
        """
        self.counters[name] = self.counters.get(name, 0) + value

    def set_gauge(self, name: str, value: float) -> None:
        """
        Set a gauge value.

        Args:
            name: Gauge name
            value: Gauge value
        """
        self.gauges[name] = value

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all metrics.

        Returns:
            Dictionary with metrics summary
        """
        total_ops = len(self.operations)
        successful_ops = sum(1 for op in self.operations if op.success)
        failed_ops = total_ops - successful_ops

        completed_ops = [op for op in self.operations if op.duration_seconds is not None]
        avg_duration = (
            sum(op.duration_seconds for op in completed_ops) / len(completed_ops)
            if completed_ops else 0
        )

        return {
            "total_operations": total_ops,
            "successful_operations": successful_ops,
            "failed_operations": failed_ops,
            "average_duration_seconds": avg_duration,
            "counters": self.counters.copy(),
            "gauges": self.gauges.copy(),
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.operations.clear()
        self.counters.clear()
        self.gauges.clear()


# Global metrics collector
_global_metrics = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    return _global_metrics


def track_time(operation_name: Optional[str] = None) -> Callable:
    """
    Decorator to track execution time of a function.

    Args:
        operation_name: Optional custom operation name

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            metrics = _global_metrics.start_operation(op_name)

            try:
                result = func(*args, **kwargs)
                metrics.complete(success=True)

                logger.debug(
                    f"Operation completed: {op_name}",
                    duration_seconds=metrics.duration_seconds
                )
                return result
            except Exception as e:
                metrics.complete(success=False, error_message=str(e))
                logger.error(
                    f"Operation failed: {op_name}",
                    error=str(e),
                    duration_seconds=metrics.duration_seconds
                )
                raise

        return wrapper
    return decorator


def track_time_async(operation_name: Optional[str] = None) -> Callable:
    """
    Decorator to track execution time of an async function.

    Args:
        operation_name: Optional custom operation name

    Returns:
        Decorated async function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            metrics = _global_metrics.start_operation(op_name)

            try:
                result = await func(*args, **kwargs)
                metrics.complete(success=True)

                logger.debug(
                    f"Async operation completed: {op_name}",
                    duration_seconds=metrics.duration_seconds
                )
                return result
            except Exception as e:
                metrics.complete(success=False, error_message=str(e))
                logger.error(
                    f"Async operation failed: {op_name}",
                    error=str(e),
                    duration_seconds=metrics.duration_seconds
                )
                raise

        return wrapper
    return decorator


class TokenCounter:
    """Utility for counting tokens in text."""

    @staticmethod
    def estimate_tokens(text: str, model: str = "gpt") -> int:
        """
        Estimate token count for text.

        This is a simple estimation. For production, use model-specific tokenizers.

        Args:
            text: Text to count tokens for
            model: Model type (gpt, llama, etc.)

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        if not text:
            return 0

        # More accurate would be to use tiktoken or similar
        return len(text) // 4

    @staticmethod
    def track_token_usage(input_text: str, output_text: str, model: str = "gpt") -> Dict[str, int]:
        """
        Track token usage for input and output.

        Args:
            input_text: Input text
            output_text: Output text
            model: Model type

        Returns:
            Dictionary with token counts
        """
        input_tokens = TokenCounter.estimate_tokens(input_text, model)
        output_tokens = TokenCounter.estimate_tokens(output_text, model)
        total_tokens = input_tokens + output_tokens

        # Update global metrics
        _global_metrics.increment_counter("total_tokens_used", total_tokens)
        _global_metrics.increment_counter("input_tokens_used", input_tokens)
        _global_metrics.increment_counter("output_tokens_used", output_tokens)

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }


class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(self, operation_name: str):
        """
        Initialize performance timer.

        Args:
            operation_name: Name of the operation being timed
        """
        self.operation_name = operation_name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None

    def __enter__(self) -> "PerformanceTimer":
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Stop timing and log."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

        logger.debug(
            f"Performance: {self.operation_name}",
            duration_seconds=self.duration,
            success=exc_type is None
        )

