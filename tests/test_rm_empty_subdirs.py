import os
import runpy
from pathlib import Path
import tempfile
import pytest

# Load the script from docker/bin (no .py extension)
MODULE_PATH = Path(__file__).resolve().parents[1] / "docker" / "bin" / "rm_empty_subdirs"
rm_module = runpy.run_path(str(MODULE_PATH))
remove_empty_directories = rm_module["remove_empty_directories"]


def test_remove_empty_directories_basic():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # non-empty directory with a file and an empty subdir
        dir1 = root / "dir1"
        dir1.mkdir()
        (dir1 / "file.txt").write_text("data")
        (dir1 / "empty").mkdir()

        # directory tree that will become entirely empty
        (root / "dir2" / "sub" / "child").mkdir(parents=True)

        # completely empty directory
        (root / "dir3").mkdir()

        rel_root = os.path.relpath(root, Path.cwd())
        remove_empty_directories(rel_root)

        assert dir1.exists()
        assert not (dir1 / "empty").exists()
        assert not (root / "dir2").exists()
        assert not (root / "dir3").exists()
        # root should still exist
        assert root.exists()


def test_allow_initial_delete():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a" / "b").mkdir(parents=True)
        rel_root = os.path.relpath(root, Path.cwd())
        remove_empty_directories(rel_root, allow_initial_delete=True)
        assert not root.exists()


def test_ignore_nonexistent_dir():
    with tempfile.TemporaryDirectory() as tmp:
        missing = Path(tmp) / "missing"
        rel_missing = os.path.relpath(missing, Path.cwd())
        with pytest.raises(RuntimeError):
            remove_empty_directories(rel_missing)
        # Should not raise when ignoring
        remove_empty_directories(rel_missing, ignore_nonexistant_initial=True)


