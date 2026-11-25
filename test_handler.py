from handler import check_file


def test_good_file_is_accepted():
    assert check_file("design.pdf", 1000) == (True, "ok")


def test_wrong_type_is_rejected():
    ok, reason = check_file("virus.exe", 1000)
    assert ok is False
    assert reason == "file type not allowed"


def test_big_file_is_rejected():
    ok, reason = check_file("poster.png", 10 * 1024 * 1024)
    assert ok is False
    assert reason == "file is too large"


def test_missing_extension_is_rejected():
    ok, _ = check_file("notes", 100)
    assert ok is False