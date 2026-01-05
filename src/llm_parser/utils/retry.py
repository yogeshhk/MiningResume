"""
Retry utility with exponential backoff.

Provides decorators and functions for retrying operations with configurable strategies.
"""

import time
import functools
from typing import Callable, Type, Tuple, Optional, Any
from ..utils.logger import get_logger
from ..core.exceptions import RetryExhaustedError

logger = get_logger(__name__)


def retry_with_backoff(
    max_attempts: int = 3,
    initial_wait: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable:
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds
        backoff_factor: Multiplier for wait time on each retry
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback called on each retry with (exception, attempt_number)

    Returns:
        Decorated function with retry logic

    Raises:
        RetryExhaustedError: When all retry attempts are exhausted
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            wait_time = initial_wait

            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1

                    if attempt >= max_attempts:
                        logger.error(
                            f"Retry exhausted for {func.__name__}",
                            max_attempts=max_attempts,
                            last_error=str(e)
                        )
                        raise RetryExhaustedError(
                            f"Failed after {max_attempts} attempts: {str(e)}",
                            details={
                                "function": func.__name__,
                                "attempts": max_attempts,
                                "last_error": str(e)
                            }
                        ) from e

                    logger.warning(
                        f"Retry attempt {attempt}/{max_attempts} for {func.__name__}",
                        error=str(e),
                        wait_time=wait_time
                    )

                    if on_retry:
                        on_retry(e, attempt)

                    time.sleep(wait_time)
                    wait_time *= backoff_factor

            # Should never reach here, but for type safety
            raise RetryExhaustedError(f"Unexpected retry loop exit for {func.__name__}")

        return wrapper
    return decorator


def retry_async_with_backoff(
    max_attempts: int = 3,
    initial_wait: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator for async functions with retry and exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds
        backoff_factor: Multiplier for wait time on each retry
        exceptions: Tuple of exception types to catch and retry

    Returns:
        Decorated async function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            import asyncio

            attempt = 0
            wait_time = initial_wait

            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1

                    if attempt >= max_attempts:
                        logger.error(
                            f"Async retry exhausted for {func.__name__}",
                            max_attempts=max_attempts,
                            last_error=str(e)
                        )
                        raise RetryExhaustedError(
                            f"Failed after {max_attempts} attempts: {str(e)}",
                            details={
                                "function": func.__name__,
                                "attempts": max_attempts,
                                "last_error": str(e)
                            }
                        ) from e

                    logger.warning(
                        f"Async retry attempt {attempt}/{max_attempts} for {func.__name__}",
                        error=str(e),
                        wait_time=wait_time
                    )

                    await asyncio.sleep(wait_time)
                    wait_time *= backoff_factor

            raise RetryExhaustedError(f"Unexpected retry loop exit for {func.__name__}")

        return wrapper
    return decorator


class RetryContext:
    """Context manager for retry operations."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_wait: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
    ):
        """
        Initialize retry context.

        Args:
            max_attempts: Maximum number of retry attempts
            initial_wait: Initial wait time in seconds
            backoff_factor: Multiplier for wait time on each retry
            exceptions: Tuple of exception types to catch and retry
        """
        self.max_attempts = max_attempts
        self.initial_wait = initial_wait
        self.backoff_factor = backoff_factor
        self.exceptions = exceptions
        self.attempt = 0
        self.last_error: Optional[Exception] = None

    def __enter__(self):
        """Enter the retry context."""
        self.attempt += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the retry context and handle retries."""
        if exc_type is None:
            return True

        if exc_type in self.exceptions:
            self.last_error = exc_val

            if self.attempt >= self.max_attempts:
                return False  # Let the exception propagate

            wait_time = self.initial_wait * (self.backoff_factor ** (self.attempt - 1))
            logger.warning(
                f"Retry attempt {self.attempt}/{self.max_attempts}",
                error=str(exc_val),
                wait_time=wait_time
            )

            time.sleep(wait_time)
            return False  # Suppress exception for retry

        return False  # Don't suppress unexpected exceptions

