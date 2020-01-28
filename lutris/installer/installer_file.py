"""Manipulates installer files"""
import os
from lutris import pga
from lutris import settings
from lutris.installer.errors import ScriptingError
from lutris.util.log import logger
from lutris.util import system
from lutris import cache


class InstallerFile:
    """Representation of a file in the `files` sections of an installer"""
    def __init__(self, game_slug, file_id, file_meta):
        self.game_slug = game_slug
        self.id = file_id  # pylint: disable=invalid-name
        if isinstance(file_meta, dict):
            for field in ("url", "filename"):
                if field not in file_meta:
                    raise ScriptingError(
                        "missing field `%s` for file `%s`" % (field, file_id)
                    )
            self.url = file_meta["url"]
            self.filename = file_meta["filename"]
            self.referer = file_meta.get("referer")
            self.checksum = file_meta.get("checksum")
        else:
            self.url = file_meta
            self.filename = os.path.basename(file_meta)
            self.referer = None
            self.checksum = None
        self.dest_file = os.path.join(self.cache_path, self.filename)

        if self.url.startswith(("$STEAM", "$WINESTEAM")):
            self.filename = self.url

        if self.url.startswith("/"):
            self.url = "file://" + self.url

        if not self.filename:
            logger.error("Couldn't find a filename for file %s in %s", file_id, file_meta)
            raise ScriptingError(
                "No filename provided for %s, please provide 'url' "
                "and 'filename' parameters in the script" % file_id
            )
        if self.uses_pga_cache(create=True):
            logger.debug("Using cache path %s", self.cache_path)

    def __str__(self):
        return "%s/%s" % (self.game_slug, self.id)

    def uses_pga_cache(self, create=False):
        """Determines whether the installer files are stored in a PGA cache

        Params:
            create (bool): If a cache is active, auto create directories if needed
        Returns:
            bool
        """
        cache_path = cache.get_cache_path()
        if not cache_path:
            return False
        if system.path_exists(cache_path):
            return True
        if create:
            try:
                os.makedirs(self.cache_path)
            except OSError as ex:
                logger.error("Failed to created cache path: %s", ex)
                return False
            return True
        logger.warning("Cache path %s does not exist", cache_path)
        return False

    @property
    def cache_path(self):
        """Return the directory used as a cache for the duration of the installation"""
        _cache_path = cache.get_cache_path()
        if not _cache_path:
            _cache_path = os.path.join(settings.CACHE_DIR, "installer")
        if "cdn.gog.com" in self.url or "cdn-hw.gog.com" in self.url:
            folder = "gog"
        else:
            folder = self.id
        return os.path.join(_cache_path, self.game_slug, folder)

    def prepare(self):
        """Prepare the file for download"""
        if not system.path_exists(self.cache_path):
            os.makedirs(self.cache_path)

    def pga_uri(self):
        """Return the URI of the file stored in the PGA
        This isn't used yet, it looks in the PGA sources
        """
        return pga.check_for_file(self.game_slug, self.id)

    def check_hash(self):
        """Checks the checksum of `file` and compare it to `value`

        Args:
            checksum (str): The checksum to look for (type:hash)
            dest_file (str): The path to the destination file
            dest_file_uri (str): The uri for the destination file
        """
        if not self.checksum or not self.dest_file:
            return
        try:
            hash_type, expected_hash = self.checksum.split(':', 1)
        except ValueError:
            raise ScriptingError("Invalid checksum, expected format (type:hash) ", self.checksum)

        if system.get_file_checksum(self.dest_file, hash_type) != expected_hash:
            raise ScriptingError(hash_type.capitalize() + " checksum mismatch ", self.checksum)

    @property
    def is_cached(self):
        """Is the file available in the local PGA cache?"""
        return self.uses_pga_cache() and system.path_exists(self.dest_file)
