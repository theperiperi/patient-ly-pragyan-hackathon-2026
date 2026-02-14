"""
FHIR Profile Loader

Loads and caches ABDM FHIR profiles from the profiles directory.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ProfileLoader:
    """Loads and caches ABDM FHIR StructureDefinition profiles."""

    def __init__(self, profiles_dir: str):
        """
        Initialize profile loader.

        Args:
            profiles_dir: Path to directory containing FHIR profile JSON files
        """
        self.profiles_dir = Path(profiles_dir)
        self._profiles_cache: Dict[str, dict] = {}
        self._profile_index: Dict[str, str] = {}  # name -> file path
        self._loaded = False

        logger.info(f"ProfileLoader initialized with directory: {self.profiles_dir}")

    def load_profiles(self) -> None:
        """
        Load all FHIR profiles from the profiles directory.

        Scans the profiles directory for StructureDefinition JSON files and
        caches them in memory.
        """
        if self._loaded:
            logger.debug("Profiles already loaded, skipping")
            return

        if not self.profiles_dir.exists():
            logger.error(f"Profiles directory does not exist: {self.profiles_dir}")
            raise FileNotFoundError(f"Profiles directory not found: {self.profiles_dir}")

        logger.info(f"Loading profiles from: {self.profiles_dir}")

        # Find all StructureDefinition JSON files
        profile_files = list(self.profiles_dir.glob("StructureDefinition-*.json"))
        logger.info(f"Found {len(profile_files)} StructureDefinition files")

        loaded_count = 0
        for profile_file in profile_files:
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)

                # Validate it's a StructureDefinition
                if profile_data.get("resourceType") != "StructureDefinition":
                    logger.warning(f"Skipping non-StructureDefinition file: {profile_file.name}")
                    continue

                profile_name = profile_data.get("name") or profile_data.get("id")
                profile_url = profile_data.get("url")

                if not profile_name:
                    logger.warning(f"Profile missing name/id: {profile_file.name}")
                    continue

                # Cache profile by name and URL
                self._profiles_cache[profile_name] = profile_data
                if profile_url:
                    self._profiles_cache[profile_url] = profile_data

                self._profile_index[profile_name] = str(profile_file)

                loaded_count += 1
                logger.debug(f"Loaded profile: {profile_name}")

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON in {profile_file.name}: {e}")
            except Exception as e:
                logger.error(f"Error loading profile {profile_file.name}: {e}")

        self._loaded = True
        logger.info(f"Successfully loaded {loaded_count} FHIR profiles")

    def get_profile(self, profile_name_or_url: str) -> Optional[dict]:
        """
        Get a profile by name or URL.

        Args:
            profile_name_or_url: Profile name (e.g., "Patient") or URL

        Returns:
            Profile StructureDefinition dict or None if not found
        """
        if not self._loaded:
            self.load_profiles()

        return self._profiles_cache.get(profile_name_or_url)

    def list_profiles(self) -> List[dict]:
        """
        List all available profiles.

        Returns:
            List of profile summaries with name, URL, type, and version
        """
        if not self._loaded:
            self.load_profiles()

        profiles = []
        seen = set()

        for profile_name, profile_data in self._profiles_cache.items():
            # Avoid duplicates (profiles cached by both name and URL)
            profile_url = profile_data.get("url")
            if profile_url in seen:
                continue

            seen.add(profile_url)

            profiles.append({
                "name": profile_data.get("name"),
                "id": profile_data.get("id"),
                "url": profile_url,
                "type": profile_data.get("type"),
                "version": profile_data.get("version"),
                "description": profile_data.get("description", "")[:200]  # Truncate
            })

        # Sort by name
        profiles.sort(key=lambda p: p.get("name", ""))

        return profiles

    def get_profile_for_resource_type(self, resource_type: str) -> Optional[dict]:
        """
        Get the ABDM profile for a specific FHIR resource type.

        Args:
            resource_type: FHIR resource type (e.g., "Patient", "Bundle", "Observation")

        Returns:
            Profile StructureDefinition or None if not found
        """
        if not self._loaded:
            self.load_profiles()

        # Try direct match first
        profile = self.get_profile(resource_type)
        if profile:
            return profile

        # Search for profiles matching the resource type
        for profile_data in self._profiles_cache.values():
            if profile_data.get("type") == resource_type:
                return profile_data

        logger.warning(f"No profile found for resource type: {resource_type}")
        return None

    def is_loaded(self) -> bool:
        """Check if profiles have been loaded."""
        return self._loaded

    def get_profiles_count(self) -> int:
        """Get count of loaded profiles."""
        # Divide by 2 because profiles are cached by both name and URL
        return len(set(p.get("url") for p in self._profiles_cache.values() if p.get("url")))


# Global profile loader instance (initialized in main.py)
_profile_loader: Optional[ProfileLoader] = None


def init_profile_loader(profiles_dir: str) -> ProfileLoader:
    """
    Initialize global profile loader.

    Args:
        profiles_dir: Path to profiles directory

    Returns:
        ProfileLoader instance
    """
    global _profile_loader
    _profile_loader = ProfileLoader(profiles_dir)
    _profile_loader.load_profiles()
    return _profile_loader


def get_profile_loader() -> Optional[ProfileLoader]:
    """
    Get global profile loader instance.

    Returns:
        ProfileLoader or None if not initialized
    """
    return _profile_loader
