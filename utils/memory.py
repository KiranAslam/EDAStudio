import psutil

from config.limits import LIMITS


def check_upload_feasibility(uploaded_file) -> tuple[bool, str]:
    file_size_mb = uploaded_file.size / (1024**2)
    if file_size_mb > LIMITS["MAX_FILE_SIZE_MB"]:
        return False, (
            f"File size ({file_size_mb:.1f} MB) exceeds the "
            f"{LIMITS['MAX_FILE_SIZE_MB']} MB limit."
        )
    available_mb = psutil.virtual_memory().available / (1024**2)
    estimated_memory_mb = file_size_mb * 7
    if estimated_memory_mb > available_mb * 0.6:
        return False, (
            f"Insufficient memory. Estimated need: {estimated_memory_mb:.0f} MB. "
            f"Available: {available_mb:.0f} MB."
        )
    return True, ""
