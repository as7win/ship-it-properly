ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg"}
MAX_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB


def check_file(filename, size_bytes):
    """Return (True, "ok") if the file is allowed, otherwise (False, reason)."""
    if not filename or "." not in filename:
        return False, "file needs a name and an extension"

    extension = "." + filename.rsplit(".", 1)[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        return False, "file type not allowed"

    if size_bytes > MAX_SIZE_BYTES:
        return False, "file is too large"

    return True, "ok"