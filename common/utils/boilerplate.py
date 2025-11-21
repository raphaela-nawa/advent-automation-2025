#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from pathlib import Path

def load_secrets(day=None, allow_defaults=False):
    """
    Load API keys for day-specific projects.

    IMPORTANT FOR CLIENT DEPLOYMENT:
    - When day is specified, ONLY day-specific keys are loaded (no fallback)
    - This ensures clients use their own keys and prevents accidental usage of dev keys
    - Defaults are ONLY used for development/testing (when allow_defaults=True)

    Args:
        day (int, optional): Day number (1-25) for day-specific keys.
                            If None, only default keys are loaded.
        allow_defaults (bool): Allow fallback to KEY_OPENAI/KEY_ANTHROPIC when
                              day-specific keys are missing. Default: False.
                              Set to True only for development/testing.

    Returns:
        dict: Dictionary with 'openai', 'anthropic', 'project_id', 'day', and 'using_defaults'

    Example (Production - Client Usage):
        >>> keys = load_secrets(day=1)
        >>> # Requires KEY_OPENAI_DAY01 and KEY_ANTHROPIC_DAY01
        >>> # Will NOT fallback to defaults

    Example (Development - Your Testing):
        >>> keys = load_secrets(day=1, allow_defaults=True)
        >>> # Uses KEY_OPENAI_DAY01 or falls back to KEY_OPENAI
    """
    # Load from config/.env relative to project root
    env_path = Path(__file__).parent.parent.parent / "config" / ".env"
    load_dotenv(env_path)

    if day:
        # Day-specific keys (REQUIRED for client projects)
        key_openai = os.getenv(f"KEY_OPENAI_DAY{day:02d}")
        key_anthropic = os.getenv(f"KEY_ANTHROPIC_DAY{day:02d}")

        # Fallback logic (only if explicitly allowed for dev/testing)
        using_defaults = False
        if allow_defaults:
            if not key_openai:
                key_openai = os.getenv("KEY_OPENAI")
                using_defaults = True
            if not key_anthropic:
                key_anthropic = os.getenv("KEY_ANTHROPIC")
                using_defaults = True

        project_id = f"day{day:02d}"
    else:
        # Only default keys (for general development/testing)
        key_openai = os.getenv("KEY_OPENAI")
        key_anthropic = os.getenv("KEY_ANTHROPIC")
        project_id = "default"
        using_defaults = True

    return {
        "openai": key_openai,
        "anthropic": key_anthropic,
        "project_id": project_id,
        "day": day,
        "using_defaults": using_defaults
    }


def validate_keys(keys, required=None, strict_mode=True):
    """
    Validate that required API keys are present.

    Args:
        keys (dict): Dictionary of API keys
        required (list, optional): List of required providers. Defaults to all.
        strict_mode (bool): If True, raises error when day-specific project uses defaults.
                           This prevents clients from accidentally using dev keys.

    Returns:
        bool: True if all required keys are present

    Raises:
        ValueError: If required keys are missing or strict_mode violations occur
    """
    if required is None:
        required = ["openai", "anthropic"]

    missing = [provider for provider in required if not keys.get(provider)]

    if missing:
        if keys.get("day"):
            # Provide helpful message for day-specific projects
            day_num = keys["day"]
            suggestion = f"KEY_OPENAI_DAY{day_num:02d} and KEY_ANTHROPIC_DAY{day_num:02d}"
            raise ValueError(
                f"Missing API keys for: {', '.join(missing)}\n"
                f"For Day {day_num:02d}, please configure: {suggestion} in config/.env"
            )
        else:
            raise ValueError(f"Missing API keys for: {', '.join(missing)}")

    # Strict mode: Warn if day-specific project is using defaults
    if strict_mode and keys.get("day") and keys.get("using_defaults"):
        raise ValueError(
            f"⚠️  SECURITY WARNING: Day {keys['day']:02d} is using default keys!\n"
            f"   This is dangerous for production/client deployments.\n"
            f"   Please configure day-specific keys:\n"
            f"   - KEY_OPENAI_DAY{keys['day']:02d}\n"
            f"   - KEY_ANTHROPIC_DAY{keys['day']:02d}\n\n"
            f"   For development/testing only, use: load_secrets(day={keys['day']}, allow_defaults=True)"
        )

    return True


def get_client(provider, day=None):
    """
    Get configured API client for a specific provider.

    Args:
        provider (str): 'openai' or 'anthropic'
        day (int, optional): Day number for day-specific keys

    Returns:
        Configured client instance

    Raises:
        ValueError: If provider is not supported or key is missing
    """
    keys = load_secrets(day=day)

    if provider == "openai":
        if not keys["openai"]:
            raise ValueError("OpenAI API key not found")
        try:
            from openai import OpenAI
            return OpenAI(api_key=keys["openai"])
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    elif provider == "anthropic":
        if not keys["anthropic"]:
            raise ValueError("Anthropic API key not found")
        try:
            from anthropic import Anthropic
            return Anthropic(api_key=keys["anthropic"])
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

    else:
        raise ValueError(f"Unsupported provider: {provider}. Use 'openai' or 'anthropic'")
