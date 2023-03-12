"""D8VK helper module"""
import os
import shutil

from lutris import api
from lutris.settings import RUNTIME_DIR
from lutris.util.extract import extract_archive
from lutris.util.http import download_file
from lutris.util.log import logger
from lutris.util.system import create_folder, execute, remove_folder
from lutris.util.wine.dll_manager import DLLManager


class D8VKManager(DLLManager):
    component = "D8VK"
    base_dir = os.path.join(RUNTIME_DIR, "d8vk")
    versions_path = os.path.join(base_dir, "d8vk_versions.json")
    managed_dlls = ("d3d8", "d3d9", )
    releases_url = "https://api.github.com/repos/AlpyneDreams/d8vk/releases"