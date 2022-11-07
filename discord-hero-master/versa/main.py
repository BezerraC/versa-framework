"""Main entry point for running versa-framework

versa-framework: A framework to make discord bots

:copyright: (c) 2022 devcbezerra.
:license: Apache-2.0 OR MIT
"""

import asyncio
import io
import os
import sys

import django
import versa
from django.core import management
from django.db import OperationalError, ProgrammingError
from versa.cli import confirm, launch, prompt, style
from versa.conf import Config, get_extension_config


def main(test, **kwargs):
    # check configuration and request missing information from user

    # dotenv config values
    os.environ['PROD'] = str(not test)
    if test:
        os.environ['PYTHONASYNCIODEBUG'] = '1'
    os.environ.update({key: str(value) for key, value in kwargs.items() if value is not None})

    # TODO custom prompt function based on click's that asks for config details that aren't given

    database_type = os.getenv('DB_TYPE')
    if database_type != 'sqlite' and not os.getenv('DB_HOST'):
        os.environ['DB_HOST'] = prompt("DB host", value_proc=str, default='localhost')
        os.environ['DB_PORT'] = prompt("DB port", value_proc=str,
                                       default='5432' if database_type == 'postgres'
                                       else '3306' if database_type == 'mysql' else None)
        os.environ['DB_NAME'] = prompt("DB name", value_proc=str)
        os.environ['DB_USER'] = prompt("DB user", value_proc=str)
        os.environ['DB_PASSWORD'] = prompt("DB password", value_proc=str, hide_input=True)

    cache_type = os.getenv('CACHE_TYPE')
    if os.getenv('CACHE_TYPE') != 'simple' and not os.getenv('CACHE_HOST'):
        os.environ['CACHE_HOST'] = prompt("Cache host", value_proc=str, default='localhost')
        os.environ['CACHE_PORT'] = prompt("Cache port", value_proc=str,
                                          default='6379' if cache_type == 'redis' else None)
        os.environ['CACHE_PASSWORD'] = input("Cache password: ")
        os.environ['CACHE_DB'] = prompt("Cache number", value_proc=str, default='0')

    if not os.getenv('BOT_TOKEN'):
        if sys.platform in ('win32', 'cygwin', 'darwin'):
            if confirm("You need a bot token for your bot. Do you want to create a "
                       "bot now? (This will open a browser window/tab.)"):
                launch("https://discordapp.com/developers/applications/")
        os.environ['BOT_TOKEN'] = input("Bot token: ")

    config = Config(test)
    config.save()

    # automatically initialize database if using SQLite for convenience
    if database_type == 'sqlite':
        if ((test and not os.path.isfile(os.path.join(versa.ROOT_DIR, "test_db.sqlite3")))
            or (not test and not os.path.isfile(os.path.join(versa.ROOT_DIR, "db.sqlite3")))):
            print("Running `versa dbinit`")
            database_initialization(test, from_main=True, **kwargs)
            print("You can now use `versa` to run your Discord versa instance.")
            return

    # load extensions
    with open(os.path.join(versa.ROOT_DIR, 'extensions.txt')) as extensions_file:
        extensions = extensions_file.read().splitlines()
        os.environ['EXTENSIONS'] = ';'.join(extensions)
    with open(os.path.join(versa.ROOT_DIR, 'local_extensions.txt')) as local_extensions_file:
        local_extensions = local_extensions_file.read().splitlines()
        os.environ['LOCAL_EXTENSIONS'] = ';'.join(local_extensions)

    configs = []
    for extension in extensions:
        configs.append(get_extension_config(extension))
    for local_extension in local_extensions:
        configs.append(get_extension_config(local_extension, local=True))

    installed_apps = []
    for _config in configs:
        installed_apps.append(f"{_config.__module__}.{_config.__name__}")
    os.environ['INSTALLED_APPS'] = ';'.join(installed_apps)

    versa.TEST = test

    # setup cache
    versa.cache.init()

    # setup django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "versa.django_settings")
    django.setup(set_prefix=False)

    # setup asyncio loop
    try:
        # noinspection PyUnresolvedReferences
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    loop = asyncio.get_event_loop()

    from versa.models import CoreSettings

    # db config values
    try:
        settings, created = CoreSettings.get_or_create(name=os.getenv('NAMESPACE'))
    except (OperationalError, ProgrammingError):
        if database_type != 'sqlite':
            print("Running `versa dbinit`")
            database_initialization(test, from_main=True, **kwargs)
            print("You can now use `versa` to run your Discord versa instance.")
            return
        raise
    if created:
        settings.prefixes = [prompt("Bot command prefix", value_proc=str, default='!')]
        settings.description = prompt("Short description of your bot", value_proc=str, default='')
        settings.save()

    with versa.Core(config=config, settings=settings, name=os.getenv('NAMESPACE', 'default'), loop=loop) as core:
        core.run()


def database_initialization(test, *, from_main=False, **kwargs):
    if not from_main:
        os.environ['PROD'] = str(not test)
        os.environ.update({key: str(value) for key, value in kwargs.items() if value is not None})

        database_type = os.getenv('DB_TYPE')
        if database_type != 'sqlite':
            os.environ['DB_HOST'] = prompt("DB host", value_proc=str, default='localhost')
            os.environ['DB_PORT'] = prompt("DB port", value_proc=str,
                                           default='5432' if database_type == 'postgres'
                                           else '3306' if database_type == 'mysql' else None)
            os.environ['DB_NAME'] = prompt("DB name", value_proc=str)
            os.environ['DB_USER'] = prompt("DB user", value_proc=str)
            os.environ['DB_PASSWORD'] = prompt("DB password", value_proc=str, hide_input=True)

    # setup django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "versa.django_settings")
    django.setup(set_prefix=False)

    print(f"Initializing database...", end=' ')
    # temporarily silence stdout while we sync the database
    backup_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        management.call_command('makemigrations', 'versa', interactive=False)
        management.call_command('makemigrations', 'versa', interactive=False, merge=True)
        try:
            management.call_command('migrate', 'versa', interactive=False)
        except management.CommandError:
            management.call_command('migrate', 'versa', interactive=False, run_syncdb=True)
    except management.CommandError as command_error:
        print(command_error, file=sys.stderr)
        return False
    else:
        print(style("OK", fg='green'), file=backup_stdout)
        return True
    finally:
        sys.stdout = backup_stdout
