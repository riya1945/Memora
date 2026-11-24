from memora.codespace import read_file,apply_edit,run_tests,git_diff
from pathlib import Path
from unittest.mock import patch
import subprocess

def test_read_file(tmp_path):
    file = tmp_path / "hello.txt" # Creates a path pointing to a file inside that directory.
    file.write_text("hi my name is riya") #Actually creates the file and writes your text into it.

    result = read_file(tmp_path, "hello.txt")

    assert result == "hi my name is riya"

def test_read_file_truncation(tmp_path):
    file = tmp_path / "hello.txt"
    file.write_text("abcdefghijklmnopqrst")

    result = read_file(tmp_path, "hello.txt", max_chars=10)

    assert result == "abcdefghij\n...[truncated]"    

def test_read_file_outside_project(tmp_path):
    result = read_file(tmp_path, "../outside.txt")

    assert result == "Path is outside the project"    
def test_read_nonexistent_file(tmp_path):
    result = read_file(tmp_path, "missing.py")

    assert result == "Output is not a file"    

def test_read_file_negative_max_chars(tmp_path):
    result = read_file(tmp_path, "hello.txt", max_chars=-10)

    assert result == "max_chars must be non-negative."

def test_read_file_invalid_max_chars_type(tmp_path):
    result = read_file(tmp_path, "hello.txt", max_chars=10.5)

    assert result == "max_chars must be an integer."

def test_read_file_permission_error(tmp_path):
    file = tmp_path / "hello.txt"
    file.write_text("hello")

    with patch.object(Path, "read_text", side_effect=PermissionError):
        result = read_file(tmp_path, "hello.txt")

    assert result == "Could not access the file"

def test_read_file_unicode_error(tmp_path):
    file = tmp_path / "hello.txt"
    file.write_text("hello")

    error = UnicodeDecodeError(
        "utf-8", b"\xff", 0, 1, "invalid start byte"
    )

    with patch.object(Path, "read_text", side_effect=error):
        result = read_file(tmp_path, "hello.txt")

    assert result == "Could not read the file"

def test_read_directory(tmp_path):
    result = read_file(tmp_path, ".")

    assert result == "Output is not a file"    

def test_apply_edit_permission_error(tmp_path):
    file = tmp_path / "hello.txt"
    file.write_text("original content")

    with patch.object(Path, "write_text", side_effect=PermissionError):
        result = apply_edit(tmp_path, "hello.txt", "new content")

    assert result == "Could not access the file"    

def test_apply_edit_permission_error_preserves_original(tmp_path):
    file = tmp_path / "hello.txt"
    file.write_text("original content")

    with patch.object(Path, "write_text", side_effect=PermissionError):
        result = apply_edit(tmp_path, "hello.txt", "new content")

    assert result == "Could not access the file"
    assert file.read_text(encoding="utf-8") == "original content"    

def test_apply_edit_outside_project(tmp_path):
    result = apply_edit(tmp_path, "../outside.txt", "new content")

    assert result == "Path is outside the project"    

def test_apply_edit_blocked_file(tmp_path):
    file = tmp_path / ".env"
    file.write_text("SECRET=value")

    result = apply_edit(tmp_path, ".env", "NEW=value")

    assert result == "Path is blocked"
    assert file.read_text(encoding="utf-8") == "SECRET=value"    

def test_apply_edit_nonexistent_file(tmp_path):
    result = apply_edit(tmp_path, "missing.txt", "new content")

    assert result == "File does not exist"
    assert not (tmp_path / "missing.txt").exists()

def test_apply_edit_directory(tmp_path):
    result = apply_edit(tmp_path, ".", "new content")

    assert result == "File does not exist"    

def test_run_tests_invalid_directory(tmp_path):
    invalid_path = tmp_path / "missing_project"

    result = run_tests(invalid_path)

    assert result == "Invalid project directory"    

def test_run_tests_success(tmp_path):
    test_file = tmp_path / "test_sample.py"
    test_file.write_text(
        "def test_example():\n"
        "    assert 1 + 1 == 2\n"
    )

    result = run_tests(tmp_path)

    assert result["status"] == "passed"
    assert "1 passed" in result["output"]

def test_run_tests_failure(tmp_path):
    test_file = tmp_path / "test_sample.py"
    test_file.write_text(
        "def test_example():\n"
        "    assert 1 + 1 == 3\n"
    )

    result = run_tests(tmp_path)

    assert result["status"] == "failed"
    assert "1 failed" in result["output"]

def test_run_tests_timeout(tmp_path):
    with patch(
        "memora.codespace.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="pytest", timeout=120)
    ):
        result = run_tests(tmp_path)

    assert result == "Tests timed out after 120 seconds"

def test_invalid_dir(tmp_path):
    result = git_diff(tmp_path / "missing")
    assert result=="Invalid project directory"   
    
def test_git_diff_timeout(tmp_path):
    with patch(
        "memora.codespace.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="git", timeout=30)
    ):
        result = git_diff(tmp_path)

    assert result == "Git diff timed out after 30 seconds"