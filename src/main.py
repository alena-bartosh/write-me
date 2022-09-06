#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path

import coloredlogs
import pandas as pd

from files_provider import FilesProvider
from html_telegram_messages_parser import HtmlTelegramMessagesParser


def main() -> None:
    parser = argparse.ArgumentParser(description=f'[write-me] Write & analyze your Telegram messages')
    parser.add_argument('--log-level', type=str, choices=['debug', 'info', 'warning', 'error'],
                        default='debug', metavar='', help='debug/info/warning/error')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('-p', '--pathdir', type=str, metavar='', help='dir with exported messages in .html',
                               required=True)

    args = parser.parse_args()

    log_level_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR
    }

    coloredlogs.install(log_level_map[args.log_level])
    logger = logging.getLogger("[write-me]")

    files_provider = FilesProvider(Path(args.pathdir), logger)
    file_paths = files_provider.get_all_raw_file_paths()

    messages: pd.DataFrame = HtmlTelegramMessagesParser.parse(file_paths)
    message_count: int = messages.shape[0]
    logger.info(f'Successfully parsed [{message_count}] messages.')

    # NOTE: Do this check here because we can have some non-empty files,
    #       but count of parsed messages still be zero because of their types
    #       (supported or not supported by out system).
    if message_count == 0:
        return

    senders: list[str] = messages.name.unique()
    dest_file_path: Path = files_provider.get_dest_file_path(senders)
    messages.to_csv(dest_file_path, sep='\t', index=False)
    logger.info(f'Save result to [{dest_file_path}].')


if __name__ == '__main__':
    main()
