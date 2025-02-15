"""Game representation for views"""
import time

from lutris.database.games import get_service_games
from lutris.game import Game
from lutris.runners import RUNNER_NAMES
from lutris.util.log import logger
from lutris.util.strings import get_formatted_playtime, gtk_safe


class StoreItem:
    """Representation of a game for views
    TODO: Fix overlap with Game class
    """

    def __init__(self, game_data, service_media):
        if not game_data:
            raise RuntimeError("No game data provided")
        self._game_data = game_data
        self.service_media = service_media

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Store id=%s slug=%s>" % (self.id, self.slug)

    @property
    def id(self):  # pylint: disable=invalid-name
        """Game internal ID"""
        # Return an unique identifier for the game.
        # Since service games are not related to lutris, use the appid
        if "service_id" not in self._game_data:
            if "appid" in self._game_data:
                return self._game_data["appid"]
            return self._game_data["slug"]

        return self._game_data["id"]

    @property
    def service(self):
        return gtk_safe(self._game_data.get("service"))

    @property
    def slug(self):
        """Slug identifier"""
        return gtk_safe(self._game_data["slug"])

    @property
    def name(self):
        """Name"""
        return gtk_safe(self._game_data["name"])

    @property
    def year(self):
        """Year"""
        return str(self._game_data.get("year") or "")

    @property
    def runner(self):
        """Runner slug"""
        return gtk_safe(self._game_data.get("runner")) or ""

    @property
    def runner_text(self):
        """Runner name"""
        return gtk_safe(RUNNER_NAMES.get(self.runner))

    @property
    def platform(self):
        """Platform"""
        _platform = self._game_data.get("platform")
        if "platform" in self._game_data:
            _platform = self._game_data["platform"]
        elif not self.service and self.installed:
            game_inst = Game(self._game_data["id"])
            if game_inst.platform:
                _platform = game_inst.platform
        return gtk_safe(_platform)

    @property
    def installed(self):
        """Game is installed"""
        if "service_id" not in self._game_data:
            return self.id in get_service_games(self.service)
        if not self._game_data.get("runner"):
            return False
        return self._game_data.get("installed")

    def get_pixbuf_path(self):
        """Returns the path to the image file for this item"""
        if self._game_data.get("icon"):
            return self._game_data["icon"]

        return self.service_media.get_absolute_path(self.slug)

    @property
    def installed_at(self):
        """Date of install"""
        return self._game_data.get("installed_at")

    @property
    def installed_at_text(self):
        """Date of install (textual representation)"""
        return gtk_safe(
            time.strftime("%X %x", time.localtime(self.installed_at)) if
            self.installed_at else ""
        )

    @property
    def lastplayed(self):
        """Date of last play"""
        return self._game_data.get("lastplayed")

    @property
    def lastplayed_text(self):
        """Date of last play (textual representation)"""
        return gtk_safe(
            time.strftime(
                "%X %x",
                time.localtime(self.lastplayed)
            ) if self.lastplayed else ""
        )

    @property
    def playtime(self):
        """Playtime duration in hours"""
        try:
            return float(self._game_data.get("playtime", 0))
        except (TypeError, ValueError):
            return 0.0

    @property
    def playtime_text(self):
        """Playtime duration in hours (textual representation)"""
        try:
            _playtime_text = get_formatted_playtime(self.playtime)
        except ValueError:
            logger.warning("Invalid playtime value %s for %s", self.playtime, self)
            _playtime_text = ""  # Do not show erroneous values
        return gtk_safe(_playtime_text)
