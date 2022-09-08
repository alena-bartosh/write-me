import nltk
import numpy as np
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
        prepared_messages['date'] = pd.to_datetime(prepared_messages['date'])
        prepared_messages['month'] = prepared_messages['date'].dt.month
        prepared_messages['year'] = prepared_messages['date'].dt.year

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
          |date|time|user|message                 |clean_words
        ------------------------------------------------------------
        0 |d   |t   |A   | want you a coffee?     |['want', 'coffee']
        1 |d+1 |t+1 |T   | no, I drink whiskey.   |['drink', 'whiskey']

        B)
          |date|time|user|message                 |clean_words
        ------------------------------------------------------------
        0 |d   |t   |A   | want you a coffee?     | want
        0 |d   |t   |A   | want you a coffee?     | coffee
        1 |d+1 |t+1 |T   | no, I drink whiskey.   | drink
        1 |d+1 |t+1 |T   | no, I drink whiskey.   | whiskey
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

    def get_popular_words(self, n: int) -> pd.DataFrame:
        """
        Return DataFrame with sorted words frequency like

          |user | word    | count
        --------------------------
        0 |A    | coffee  | 37
        1 |A    | tea     | 15
        3 |T    | whiskey | 42
        4 |T    | beer    | 1
        (here n=2)
        """
        popular_words = self.flatten_messages.groupby(['user'])['clean_words'] \
            .agg(count='value_counts') \
            .reset_index() \
            .groupby(['user']) \
            .head(n) \
            .reset_index(drop=True) \
            .rename(columns={'clean_words': 'word'})

        return popular_words

    def get_message_count(self) -> pd.DataFrame:
        return self.prepared_messages.groupby('user')['message'] \
            .agg(count='count') \
            .reset_index()

    def get_mean_message_len(self) -> pd.DataFrame:
        """
        Since use a cleaned DataFrame as input,
        shows how many informative words in average in message
        """

        res = self.flatten_messages.groupby(['index', 'user'])['clean_words'] \
            .agg(words_count='count') \
            .reset_index() \
            .groupby(['user'])['words_count'] \
            .agg(words_in_avg_by_message='mean') \
            .reset_index()
        res['count'] = res.words_in_avg_by_message.apply(np.ceil)  # round to upper

        return res

    # NOTE: In the functions below, we calculated values only for days/months/years when there were messages.
    #       If users send messages only 2 months from 12, then mean value will be (message_count / 2).
    #       So the resulting data may be speculative.

    def get_mean_per_active_day(self) -> pd.DataFrame:
        res = self.prepared_messages.groupby(['user', 'date'])['message'] \
            .agg(messages_count='count') \
            .reset_index() \
            .groupby(['user'])['messages_count'] \
            .agg(messages_in_avg_per_day='mean') \
            .reset_index()
        res['count'] = res.messages_in_avg_per_day.apply(np.ceil)  # round to upper

        return res

    def get_total_per_active_day(self) -> pd.DataFrame:
        return self.prepared_messages.groupby(['user', 'date'])['message'] \
            .agg(messages_count='count') \
            .reset_index()

    def get_mean_per_active_month(self) -> pd.DataFrame:
        res = self.prepared_messages.groupby(['user', 'month', 'year'])['message'] \
            .agg(messages_count='count') \
            .reset_index() \
            .groupby(['user', 'year'])['messages_count'] \
            .agg(messages_in_avg_per_month='mean') \
            .reset_index()
        res['count'] = res.messages_in_avg_per_month.apply(np.ceil)  # round to upper

        return res

    def get_mean_per_active_year(self) -> pd.DataFrame:
        res = self.prepared_messages.groupby(['user', 'year'])['message'] \
            .agg(messages_count='count') \
            .reset_index() \
            .groupby(['user'])['messages_count'] \
            .agg(messages_in_avg_per_year='mean') \
            .reset_index()
        res['count'] = res.messages_in_avg_per_year.apply(np.ceil)  # round to upper

        return res

    def get_active_months_per_active_year(self, n: int) -> pd.DataFrame:
        return self.prepared_messages.groupby(['user', 'month', 'year'])['message'] \
            .agg(messages_count='count') \
            .reset_index() \
            .sort_values(['messages_count'], ascending=False) \
            .groupby(['user', 'year']) \
            .head(n) \
            .reset_index(drop=True)
