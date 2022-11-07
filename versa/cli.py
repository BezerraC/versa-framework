"""versa-framework: A framework to make discord bots

:copyright: (c) 2022 devcbezerra.
:license: Apache-2.0 OR MIT
"""

import os

import click
import versa
from click import (argument, clear, confirm, echo, echo_via_pager, edit,
                   launch, option, progressbar, prompt)
from click import secho as styled_echo
from click import style
from dotenv import load_dotenv

from .main import main


def load_correct_dotenv(ctx, param, is_prod):
    file_name = '.prodenv' if is_prod else '.testenv'
    file_path = os.path.join(versa.ROOT_DIR, file_name)
    try:
        load_dotenv(file_path)
    except FileNotFoundError:
        pass
    return is_prod


@click.group(name='main', invoke_without_command=True)
@click.option('-p/-t', '--prod/--test', callback=load_correct_dotenv, default=True)
@click.option('--namespace', show_default=False,
              default=lambda: os.getenv('NAMESPACE', 'default'))
@click.option('--db-type', type=click.Choice(['sqlite', 'postgres', 'mysql'], case_sensitive=False),
              default=lambda: os.getenv('DB_TYPE', 'sqlite'))
@click.option('--db-name', default=lambda: os.getenv('DB_NAME'))
@click.option('--db-user', default=lambda: os.getenv('DB_USER'))
@click.option('--db-password', default=lambda: os.getenv('DB_PASSWORD'))
@click.option('--db-host', default=lambda: os.getenv('DB_HOST'))
@click.option('--db-port', default=lambda: os.getenv('DB_PORT'))
@click.option('--cache-type', type=click.Choice(['simple', 'redis'], case_sensitive=False),
              default=lambda: os.getenv('CACHE_TYPE', 'simple'))
@click.option('--cache-host', default=lambda: os.getenv('CACHE_HOST'))
@click.option('--cache-port', default=lambda: os.getenv('CACHE_PORT'))
@click.option('--cache-password', default=lambda: os.getenv('CACHE_PASSWORD'))
def main_cli(prod, namespace, db_type, db_name, db_user, db_password, db_host, db_port,
             cache_type, cache_host, cache_port, cache_password):
    main(test=not prod, namespace=namespace, db_type=db_type, db_name=db_name, db_user=db_user,
         db_password=db_password, db_host=db_host, db_port=db_port, cache_type=cache_type,
         cache_host=cache_host, cache_port=cache_port, cache_password=cache_password)


command = main_cli.command
group = main_cli.group
