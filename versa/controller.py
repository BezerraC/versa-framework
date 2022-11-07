"""Main entry point for running versa-framework

versa-framework: A framework to make discord bots

:copyright: (c) 2022 devcbezerra.
:license: Apache-2.0 OR MIT
"""

import versa
from aiologger.levels import LogLevel
from versa import logging


class Controller:
    def __init__(self, core: versa.Core, extension: versa.Extension, db: versa.Database, cache, settings):
        self.core = core
        self.extension = extension
        self.db = db
        self.cache = cache
        self.settings = settings
        self.log = logging.Logger.with_default_handlers(name=f"versa.extensions.{self.extension.name}.controller",
                                                        level=LogLevel.DEBUG if versa.TEST else LogLevel.INFO,
                                                        loop=self.core.loop)
