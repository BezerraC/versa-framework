"""versa-framework: A framework to make discord bots

:copyright: (c) 2022 devcbezerra.
:license: Apache-2.0 OR MIT
"""

from enum import Enum


class Languages(Enum):
    # TODO
    en_us = 'en_US'
    default = 'en_US'
    custom = 'custom'

    def __len__(self):
        return len(self.value)


def translate(s: str, translation_context=None):
    if translation_context is None:
        return s
    return translation_context.translate(s)
