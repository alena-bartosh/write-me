import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

nltk.download('stopwords')

from stop_words import RUSSIAN_STOP_WORDS, UKRAINIAN_STOP_WORDS


class MessagesManipulator:
    """
    Transform raw messages DataFrame and
    do some simple manipulations to get basic stats
    """

    @staticmethod
    def __clean_up_words(words: list[str]) -> list[str]:
        stemmer = SnowballStemmer('russian')
        clean_words = []

        for word in words:
            if len(word) <= 1:
                continue
            if word.startswith('http'):
                continue
            if word in stopwords.words(
                    ['english', 'russian']) or word in UKRAINIAN_STOP_WORDS or word in RUSSIAN_STOP_WORDS:
                continue
            clean_words.append(stemmer.stem(word))
        return clean_words

    def __prepare_messages(self) -> pd.DataFrame:
        prepared_messages = pd.DataFrame()
        prepared_messages['date'] = self.raw_messages['datetime'].dt.date
        prepared_messages['time'] = self.raw_messages['datetime'].dt.time
        prepared_messages['user'] = self.raw_messages['name']

        # Remove punctuations, make in lowercase, use stemmer
        prepared_messages['message'] = self.raw_messages['text'].str.replace('[^\w\s]', ' ').str.lower()
        prepared_messages['words'] = prepared_messages.message.str.split(' ')
        prepared_messages['clean_words'] = prepared_messages.words.apply(self.__clean_up_words)

        return prepared_messages

    def __get_flatten_messages(self) -> pd.DataFrame:
        """
        Transform prepared messages DataFrame A based on clean words column and return B.

        A)
          date|time|user|message                 |clean_words
        ------------------------------------------------------------
        0 d   |t   |A   | want you a coffee?     |['want', 'coffee']
        1 d+1 |t+1 |T   | no, I drink whiskey.   |['drink', 'whiskey']

        B)
          date|time|user|message                 |clean_words
        ------------------------------------------------------------
        0 d   |t   |A   | want you a coffee?     | want
        0 d   |t   |A   | want you a coffee?     | coffee
        1 d+1 |t+1 |T   | no, I drink whiskey.   | drink
        1 d+1 |t+1 |T   | no, I drink whiskey.   | whiskey
        """
        flatten_clean_words = pd.DataFrame(
            [[i, x] for i, y in self.prepared_messages['clean_words'].iteritems() for x in y],
            columns=['index', 'clean_words'])
        flatten_clean_words = flatten_clean_words.set_index('index')

        flatten_messages = self.prepared_messages[['date', 'time', 'user', 'message']] \
            .merge(flatten_clean_words,
                   left_index=True,
                   right_index=True)
        flatten_messages.index.name = 'index'

        return flatten_messages

    def __init__(self, raw_messages: pd.DataFrame) -> None:
        self.raw_messages = raw_messages

        expected_columns = ['date', 'name', 'text']
        if not set(expected_columns).issubset(raw_messages.columns):
            raise ValueError(f'Raw messages [dataframe={raw_messages.columns}] does not have '
                             f'one of more [required columns={expected_columns}]!')

        self.raw_messages['datetime'] = pd.to_datetime(raw_messages['date'], dayfirst=True)
        self.prepared_messages = self.__prepare_messages()
        self.flatten_messages = self.__get_flatten_messages()
