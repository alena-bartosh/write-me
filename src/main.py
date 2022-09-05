#!/usr/bin/env python3

import argparse
import glob
import logging
from pathlib import Path

import coloredlogs
import pandas as pd
from bs4 import BeautifulSoup

MESSAGES_MASK = "messages*.html"
DESTINATION_DIR = "dest"


def parse_html_messages(file_paths: list[str]) -> pd.DataFrame:
    """
    Parse only text messages. Skip pictures, audio, forwarded etc.
    Return data with the next cols: [date, name, text]
    """
    all_messages: list[dict] = []

    for message_file in file_paths:
        parsed_html = BeautifulSoup(Path(message_file).open('r').read(), features='html.parser')

        part_messages: list[dict] = []
        last_date: str | None = None
        last_name: str | None = None
        is_forwarded: bool | None = None

        for tag in parsed_html.body('div', attrs={
            'class': ['forwarded body', 'pull_right date details', 'text', 'from_name']})[1:]:
            tag_class = tag.attrs['class']

            if 'forwarded' in tag_class:
                is_forwarded = True
            elif 'pull_right' in tag_class:
                last_date = tag.attrs['title']
            elif 'text' in tag_class:
                text = tag.text.strip()
                if not is_forwarded:
                    part_messages.append(dict(date=last_date, name=last_name, text=text))
                is_forwarded = False
            elif 'from_name' in tag_class:
                last_name = tag.text.strip()
        all_messages += part_messages

    return pd.DataFrame(all_messages)


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

    messages: pd.DataFrame = parse_html_messages(file_paths)
    logger.info(f'Successfully parsed [{messages.shape[0]}] messages.')

    senders: list[str] = messages.name.unique()
    dest_file_path: str = f'{DESTINATION_DIR}/messages_' + '_'.join(senders) + '.tsv'
    messages.to_csv(dest_file_path, sep='\t', index=False)
    logger.info(f'Save result to [{dest_file_path}].')


if __name__ == '__main__':
    main()
