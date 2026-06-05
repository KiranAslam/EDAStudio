import functools
from contextlib import contextmanager
from datetime import datetime, timezone

import streamlit as st

from utils.logging_config import logger


def _render_error_card(
    title: str,
    message: str,
    error_code: str,
    exception: Exception,
    severity: str = "error",
) -> None:
    logger.error(
        "[%s] %s: %s",
        error_code,
        title,
        message,
        exc_info=True,
        extra={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_code": error_code,
            "exception_type": type(exception).__name__,
        },
    )
    severity_labels = {
        "critical": "CRITICAL",
        "error": "ERROR",
        "warning": "WARNING",
    }
    label = severity_labels.get(severity, "ERROR")
    st.error(
        f"**[{label}] {title}** (Code: `{error_code}`)\n\n{message}\n\n"
        f"*If this persists, contact support with error code `{error_code}`.*"
    )


def safe_component(fallback_message: str = "This component encountered an error."):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except MemoryError as e:
                _render_error_card(
                    title="Memory Limit Exceeded",
                    message=(
                        "The dataset is too large to process. Try a smaller file "
                        "or enable sampling."
                    ),
                    error_code="MEM_001",
                    exception=e,
                    severity="critical",
                )
            except ValueError as e:
                _render_error_card(
                    title="Data Validation Error",
                    message=str(e),
                    error_code="VAL_001",
                    exception=e,
                    severity="warning",
                )
            except Exception as e:
                _render_error_card(
                    title="Unexpected Error",
                    message=fallback_message,
                    error_code="SYS_001",
                    exception=e,
                    severity="error",
                )

        return wrapper

    return decorator


@contextmanager
def exception_boundary(operation_name: str, reraise: bool = False):
    try:
        yield
    except MemoryError:
        st.error(
            f"**Memory exhausted** during '{operation_name}'. "
            "Please reduce dataset size and try again."
        )
        logger.critical("OOM in '%s'", operation_name, exc_info=True)
        if reraise:
            raise
    except Exception as e:
        st.error(
            f"**'{operation_name}' failed**: {type(e).__name__} — {str(e)[:200]}"
        )
        logger.error("Pipeline failure in '%s'", operation_name, exc_info=True)
        if reraise:
            raise
