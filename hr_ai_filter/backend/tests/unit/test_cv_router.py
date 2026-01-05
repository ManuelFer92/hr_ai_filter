from pathlib import Path

from backend.app.routers import cv_router
from backend.app.utils.paths import DATA_DIR


def test_cv_dir_location():
    assert str(cv_router.CV_DIR).startswith(str(Path(DATA_DIR)))
    assert not str(cv_router.CV_DIR).startswith("/app"), "CV_DIR should not point to /app"
