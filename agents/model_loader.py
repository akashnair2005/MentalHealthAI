import logging
import os
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)

# Resolve the project root directory based on this file's location:
# agents/model_loader.py -> project root is one level up
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Allow overriding the model path via environment variable.
# If the value is an absolute path it is used as-is; otherwise it is
# treated as relative to the project root.
_env_model_path = os.environ.get("EMOTION_MODEL_PATH", "models/emotion_model.pkl")
_env_path_obj = Path(_env_model_path)
_MODEL_PATH = _env_path_obj if _env_path_obj.is_absolute() else _PROJECT_ROOT / _env_path_obj

# Module-level cache so the model is only loaded once
_cached_model = None
_model_load_attempted = False


def load_emotion_model():
    """Load the emotion model from disk, with caching and graceful fallback.

    Returns the loaded model object, or None if the model file cannot be found
    or loaded.  Subsequent calls return the cached result without re-reading
    the file.
    """
    global _cached_model, _model_load_attempted

    if _model_load_attempted:
        return _cached_model

    _model_load_attempted = True

    model_path = _MODEL_PATH
    logger.info("Attempting to load emotion model from: %s", model_path)

    if not model_path.exists():
        logger.warning(
            "Emotion model file not found at '%s'. "
            "The app will fall back to keyword-based emotion detection.",
            model_path,
        )
        return None

    try:
        with open(model_path, "rb") as f:
            _cached_model = pickle.load(f)
        logger.info("Emotion model loaded successfully from: %s", model_path)
    except (OSError, pickle.UnpicklingError, EOFError) as exc:
        logger.error(
            "Failed to load emotion model from '%s': %s. "
            "The app will fall back to keyword-based emotion detection.",
            model_path,
            exc,
        )
        _cached_model = None

    return _cached_model
