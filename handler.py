ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


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



def lambda_handler(event, context):
    """Entry point that AWS Lambda calls."""
    ok, reason = check_file(event.get("filename"), event.get("size_bytes", 0))
    return {"accepted": ok, "reason": reason}