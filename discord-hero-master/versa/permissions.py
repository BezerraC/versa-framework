"""Default permissions for core models

versa-framework: A framework to make discord bots

:copyright: (c) 2022 devcbezerra.
:license: Apache-2.0 OR MIT
"""

from .perms import Groups

default_bot_permissions = {
    'core': {
        'help': {
            Groups.EVERYONE: {
                'allowed': True,
                'times': 1,
                'interval': 0.5
            }
        }
    }
}
