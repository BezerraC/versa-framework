"""
versa-framework
~~~~~~~~~~~~

A framework to make discord bots

:copyright: (c) 2022 devcbezerra.
:license: Apache-2.0 OR MIT
"""

import builtins
import logging as _logging
import os
import re
import sys
from collections import namedtuple

# enable ANSI color codes on Windows
try:
    import colorama
    colorama.init()
except ImportError:
    pass
else:
    colorama.init()

# silence aiocache warnings about optional dependencies
aiocache_logger = _logging.getLogger('aiocache.serializers.serializers')
aiocache_logger.setLevel('ERROR')


_GLOBAL_VAR_NAME = '_do_not_include_all'


def _start_all(globs):
    globs[_GLOBAL_VAR_NAME] = list(globs.keys()) + [_GLOBAL_VAR_NAME]


def _end_all(globs):
    globs['__all__'] = list(
        set(list(globs.keys())) - set(globs[_GLOBAL_VAR_NAME])
    )

from django.apps import AppConfig


class DiscordVersaConfig(AppConfig):
    name = 'versa'
    verbose_name = "Versa Framework"


_start_all(globals())

start_all = _start_all

end_all = _end_all

ROOT_DIR = os.getcwd()
"""str: The root directory of the running application.
Use in conjunction with ``os.path.join``.
"""

LIB_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
"""str: The root directory of the versa-framework library.
Use in conjunction with ``os.path.join``.
"""

_, LIB_DIR_NAME = os.path.split(os.path.dirname(LIB_ROOT_DIR))

sys.path.append(ROOT_DIR)

from .i18n import translate

builtins._ = translate

from discord.ext.commands import BucketType, Context, check, command, cooldown

# from .perms import (BotPermission, BotPermissions, BotPermissionsEnum)
from .cache import cached, get_cache
from .cog import Cog, listener
from .command import Command, Group, command, group
from .conf import Config, Extension, ExtensionConfig
from .controller import Controller
from .core import Core
from .db import Database
from .errors import ConfigurationError, InvalidArgument, ObjectDoesNotExist
from .utils import async_using_db

aiocache_logger.setLevel('WARNING')


default_app_config = f"{DiscordVersaConfig.__module__}.{DiscordVersaConfig.__name__}"


__title__ = 'versa-framework'
__author__ = 'devcbezerra.'
__license__ = 'Apache-2.0 OR MIT'
__copyright__ = 'Copyright 2022 devcbezerra.'
__version__ = '0.1.0-beta.8'
__is_release__ = LIB_DIR_NAME == 'site-packages'


VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial',
                         defaults=(0,) * 5)

version_pattern = re.compile(
    # major
    r'(0|[1-9]\d*)\.'
    # minor
    r'(0|[1-9]\d*)\.'
    # micro
    r'(0|[1-9]\d*)'
    # releaselevel
    r'?(?:'
    r'-(0|[1-9]\d*|\d*[A-Za-z][\dA-Za-z]*)'
    r')'
    # serial
    r'?(?:'
    r'\.(0|[1-9]\d*|\d*[A-Za-z][\dA-Za-z]*))*'
)


def version(_version: str):
    try:
        return VersionInfo(*re.match(version_pattern, _version).groups())
    except AttributeError:
        raise ConfigurationError(f"Invalid extension version string: {_version}\n"
                                 f"Follow semantic versioning and do NOT include "
                                 f"a leading 'v'")


def version_str(_version: VersionInfo):
    return '.'.join((_version.major, _version.minor, _version.micro))\
           + (('-' + '.'.join((_version.releaselevel, _version.serial))) if _version.releaselevel else '')


VERSION = version(__version__)

LANGUAGE = os.getenv('LANGUAGE', i18n.Languages.default)

TEST = None

end_all(globals())
