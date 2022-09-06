from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


class HtmlTelegramMessagesParser:

    @staticmethod
    def parse(file_paths: list[Path]) -> pd.DataFrame:
        """
        Parse only text messages. Skip pictures, audio, forwarded etc.
        Return data with the next cols: [date, name, text]
        """
        all_messages: list[dict] = []

        for message_file in file_paths:
            parsed_html = BeautifulSoup(message_file.open('r').read(), features='html.parser')

            part_messages: list[dict] = []
            last_date: str | None = None
            last_name: str | None = None
            is_forwarded: bool | None = None

            needed_attrs: dict[str, list[str]] = {
                'class': ['forwarded body', 'pull_right date details', 'text', 'from_name']}

            for tag in parsed_html.body('div', attrs=needed_attrs)[1:]:
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
