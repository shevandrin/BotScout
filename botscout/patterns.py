import yaml
from importlib import resources

_PATTERNS_CACHE = None


def load_patterns():
    """
        Loads and parses the patterns from the patterns.yaml file.

        This function uses a cache to ensure the file is only read once.
        It leverages importlib.resources to safely access package data.

        Returns:
            A dictionary containing all the loaded patterns.
    """
    global _PATTERNS_CACHE
    if _PATTERNS_CACHE is not None:
        return _PATTERNS_CACHE
    print("Loading heuristic patterns from file for the first time...")

    try:
        patterns_file_path = resources.files('botscout.data').joinpath('patterns.yaml')

        with patterns_file_path.open('r') as f:
            data = yaml.safe_load(f)
            _PATTERNS_CACHE = data
            return data
    except FileNotFoundError:
        print("FATAL ERROR: patterns.yaml not found!")
        return {}  # Return an empty dict to prevent crashes
    except Exception as e:
        print(f"FATAL ERROR: Could not parse patterns.yaml: {e}")
        return {}


PATTERNS = load_patterns()
COOKIE_PATTERNS = PATTERNS.get('detection', {}).get('cookie_consent', {})
