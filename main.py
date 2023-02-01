#!/usr/bin/env python3

"""ERM&CK - Enterprise Response Model & Common Knowledge.

usage:
  main.py markdown [-i | --init] (options) [-dn]
  main.py confluence [-i | --init] (options) (-t <token> | --token <token>) [-dn]
  main.py mkdocs [-i | --init] (options) [-dn]
  main.py -h | --help
  main.py -v | --version

options:
  -h, --help                Show this screen
  -i, --init                Initialize empty knowledge base
  -a, --all-entities        Build all the analytics
  --response-actions        Build response actions part
  --response-actions-impls  Build response action implementations part
  --software                Build software part
  --artifacts               Build artifacts part
  --response-playbooks      Build response playbooks part
  --usecases                Build usecases part
  --response-stages         Build response stages part
  -t TOKEN, --token TOKEN   Personal Access Token for Confluence API authentication
  -d, --debug               Run in debug mode
  -n, --no-logo             Do not show ASCII art logo
  -v, --version             Show builder version
"""

import getpass
import logging
import os
import sys
import time

from atlassian.confluence import Confluence
from docopt import docopt

from data import __version__ as DATA_VERSION
from ermack import __version__ as CODE_VERSION
from ermack.data_providers.confluence_provider import ConfluenceProvider
from ermack.data_providers.markdown_provider import MarkdownProvider
from ermack.data_providers.mkdocs_provider import MkdocsProvider
from ermack.entities.entities_map import EntitiesMap
from ermack.render_knowledge_base import DataRenderer
from ermack.utils.update_attack_mapping import UpdateAttackMapping
from ermack.utils.utils import Utils as utils
from ermack.utils.visual import logo

start_time = time.time()


def main():
    """
    Run script.

    It handles command line arguments and
    builds knowledge base according specified options
    """
    config = utils.load_config("config.yml")
    logger = logging.getLogger("ermack_logger")
    __configure_logger(config, logger)
    logger.debug(sys.argv)

    # parse args according format described in file docstring
    args = docopt(__doc__)

    if not args["--no-logo"]:
        logger.info(
            logo + f" | Code version: {CODE_VERSION}; Data version: {DATA_VERSION}"
        )

    # logger.info(f"Code version: {CODE_VERSION}; Data version: {DATA_VERSION}")

    if args["--version"]:
        return

    entities_map = EntitiesMap()

    data_provider = None

    if args["mkdocs"]:
        data_provider = MkdocsProvider(entities_map=entities_map)

    elif args["markdown"]:
        data_provider = MarkdownProvider()

    elif args["confluence"]:
        confluence = __get_confluence_api(args, config)
        data_provider = ConfluenceProvider(
            confluence=confluence, entities_map=entities_map
        )
    else:
        raise Exception("Unknown command in command line arguments")

    UpdateAttackMapping()
    renderer = DataRenderer(entities_map=entities_map, data_provider=data_provider)
    renderer.render(args=args)

    logging.info("--- %s seconds ---" % (time.time() - start_time))


def __get_confluence_api(args, config):
    confluence_url = config.get("confluence_url")
    if args["--token"]:
        logging.info("[I] Using parameter supplied Confluence PAT")
        token = args["--token"]
        confluence = Confluence(url=confluence_url, token=token)
    elif os.environ.get("CONFLUENCE_TOKEN") is not None:
        logging.info("[I] Using environment vairable supplied Confluence PAT")
        token = os.environ["CONFLUENCE_TOKEN"]
        confluence = Confluence(url=confluence_url, token=token)
    else:
        logging.info("Provide Confluence credentials\n")
        login = input("Login: ")
        password = getpass.getpass(prompt="Password: ", stream=None)
        confluence = Confluence(url=confluence_url, username=login, password=password)

    return confluence


def __configure_logger(config, logger):
    if "log_file" in config and str(config.get("log_file")) != "":
        sh = logging.StreamHandler()
        sh_formatter = logging.Formatter("%(msg)s")
        sh.setFormatter(sh_formatter)
        logger.addHandler(sh)
        fh = logging.FileHandler(filename=config.get("logfile"))
        fh.setFormatter(sh_formatter)
        logger.addHandler(fh)
        if "log_level" in config and "log_level" in logging._nameToLevel:
            logger.setLevel(level=logging._nameToLevel[config.get("log_level")])
        else:
            logger.setLevel(level=logging.INFO)
    else:
        sh = logging.StreamHandler()
        sh_formatter = logging.Formatter("%(message)s")
        sh.setFormatter(sh_formatter)
        logger.addHandler(sh)
        if "log_level" in config and "log_level" in logging._nameToLevel:
            logger.setLevel(level=logging._nameToLevel[config.get("log_level")])
        else:
            logger.setLevel(level=logging.INFO)
    logger.propagate = False


if __name__ == "__main__":
    main()
