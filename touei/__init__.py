"""Touei is a Projection management controller for projection room at an
   Anime Convention"""

__version__ = "0.1"

__all__ = ["player", "playlist", "mkvutils", "utils"]

CONFIG_DEFAULT_VALUE={"pid": "/var/pid/touei.pid",
                      "slave_socket": "/tmp/touei_slave.fifo",
                      "deamon_log": "touei_deamon.log",
                      "main_log": "touei_main.log",
                      "level": "30",
                      "seek_delay": "2",
                      "recovery_time": "70",
                      "block_duration": "60",
                      "location": "/home/video",
                      "recovery": "%(location)/recovery.mkv",
                      "standby": "%(location)/standby.mkv",
                      "intro": "%(location)/intro.mkv",
                      "outro": "%(location)/outro.mkv",
                      "countdown": "%(location)/countdown.mkv",
                      }


# Load sub modules
from mkvutils import *
from playlist import *
from player import *
# Load function
from utils import *
