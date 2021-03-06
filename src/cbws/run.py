import json
import logging
import time
import os

from argparse import ArgumentParser

from cbws.server import WebsocketServer


class _CommandLineArgError(Exception):
    """ Error parsing command-line options """
    pass


class _Options(object):
    """Options returned by _parseArgs"""

    def __init__(self, conf_file, log_level):
        """
        :param config: (str) path to JSON config file.
        :param log_level: (str) logger verbosity 'info' for logging.INFO 
            or 'debug' for logging.DEBUG.
        """
        self.conf_file = conf_file

        if log_level == 'info':
            self.log_level = logging.INFO
        elif log_level == 'debug':
            self.log_level = logging.DEBUG


def _parseArgs():
    """
    Parse command-line args
    :rtype: _Options object
    :raises _CommandLineArgError: on command-line arg error
    """

    parser = ArgumentParser(description="Start CloudBrain websocket server.")

    parser.add_argument(
        "--file",
        type=str,
        default=None,
        dest="conf_file",
        help="Path to JSON config file.")

    parser.add_argument(
        "--log",
        type=str,
        dest="log_level",
        required=False,
        default='info',
        help="OPTIONAL: logger verbosity. Can be 'info' or 'debug'.")

    options = parser.parse_args()

    return _Options(conf_file=options.conf_file, log_level=options.log_level)


def run(config_file, log_level):

    logging.basicConfig(level=log_level)

    config = {}
    if config_file:
        with open(config_file, 'rb') as f:
            config = json.load(f)
    
    port = os.environ.get("PORT", None) or config['ws_server_port']
    rabbitmq_address = os.environ.get("RABBITMQ_ADDRESS", None) or config['rabbitmq_address']
    rabbitmq_user = os.environ.get("RABBITMQ_USER", None) or config['rabbitmq_user']
    rabbitmq_pwd = os.environ.get("RABBITMQ_PWD", None) or config['rabbitmq_pwd']

    server = WebsocketServer(ws_server_port=port,
                             rabbitmq_address=rabbitmq_address,
                             rabbitmq_user=rabbitmq_user,
                             rabbitmq_pwd=rabbitmq_pwd)
    try:
        server.start()
        while 1:
            time.sleep(0.1)
    except KeyboardInterrupt:
        server.stop()


def main():
    try:
        options = _parseArgs()
        run(options.conf_file, options.log_level)
    except Exception as ex:
        logging.exception("Wesocket server failed")


if __name__ == '__main__':
    main()
