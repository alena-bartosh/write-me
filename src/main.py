#!/usr/bin/env python3

import argparse
import glob
import logging
from pathlib import Path

import coloredlogs
import pandas as pd

from html_telegram_messages_parser import HtmlTelegramMessagesParser

MESSAGES_MASK = "messages*.html"
DESTINATION_DIR = "dest"


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

    logger.debug('Try to find .html file from chat export ...')
    dir_path = Path(args.pathdir)

    if not dir_path.is_dir():
        raise ValueError(f'Path [{dir_path}] does not exist or it is not a dir!')

    file_paths = glob.glob(str(dir_path / MESSAGES_MASK))
    files_count = len(file_paths)

    if files_count == 0:
        logger.error(f'Path [{dir_path}] does not contain any files with messages!')
        return

    logger.debug(f'There are {files_count} files for parsing.')

    messages: pd.DataFrame = HtmlTelegramMessagesParser.parse(file_paths)
    logger.info(f'Successfully parsed [{messages.shape[0]}] messages.')

    senders: list[str] = messages.name.unique()
    dest_file_path: str = f'{DESTINATION_DIR}/messages_' + '_'.join(senders) + '.tsv'
    messages.to_csv(dest_file_path, sep='\t', index=False)
    logger.info(f'Save result to [{dest_file_path}].')


if __name__ == '__main__':
    main()
