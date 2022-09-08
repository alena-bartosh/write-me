import logging
from datetime import datetime
from enum import Enum
from random import choice, randint

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash import dash_table

from messages_manipulator import MessagesManipulator

COLORS_SEQUENTIALS = [
    px.colors.sequential.Viridis,
    px.colors.sequential.GnBu,
    px.colors.sequential.deep,
    px.colors.sequential.dense,
]


class ElementId(Enum):
    STATS_OUTPUT = 'stats-output'


class MessageStatsDashServer:

    def __init__(self,
                 logger: logging.Logger,
                 messages_manipulator: MessagesManipulator) -> None:
        # TODO: Add some assets files if needed
        self.app = Dash(__name__, assets_folder='./assets')

        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('parse').setLevel(logging.WARNING)
        self.app.logger = logger

        self.messages_manipulator = messages_manipulator

        self.host = 'localhost'
        self.port = 3838

        self.app.title = 'Write-me'
        self.colors = choice(COLORS_SEQUENTIALS)
        self.app.layout = self.__get_layout()

    @staticmethod
    def __generate_table(df: pd.DataFrame,
                         columns: list[dict[str, str]],
                         max_rows: int = 4) -> dash_table.DataTable:
        return dash_table.DataTable(
            id=f'datatable-interactivity-{randint(1, 1042)}',
            data=df.to_dict('records'),
            columns=columns,
            filter_action='native',
            sort_action='native',
            page_size=max_rows,
            # style
            style_header={
                'fontWeight': 'bold',
                'backgroundColor': 'rgb(230, 230, 230)',
                'border': '1px solid black'
            },
            style_cell={
                'textAlign': 'left',
                'border': '1px solid grey',
                'width': '45%',
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            fixed_rows={'headers': True},
            style_table={
                'margin-left': '3vh',
                'width': '80%'
            },
        )

    @staticmethod
    def __get_columns(is_default: bool = True, additional: list[dict] = []) -> list[dict]:
        default_cols = [
            {
                'name': 'ЮЗЕР',
                'id': 'user',
                'type': 'text'
            },
            {
                'name': 'КОЛИЧЕСТВО',
                'id': 'count',
                'type': 'numeric'
            },
        ]
        return additional + default_cols if is_default else additional

    def __get_layout(self) -> html.Div:
        """Get layout loading spinner & stats output"""
        words_frequency_text = [
            html.H3(f'{user} чаще всего использует слова [{", ".join(row.word.tolist())}].') for user, row in
            self.messages_manipulator.get_popular_words(10).groupby(['user'])
        ]

        min_date = datetime.strftime(self.messages_manipulator.prepared_messages.date.min(), "%Y-%m-%d")
        max_date = datetime.strftime(self.messages_manipulator.prepared_messages.date.max(), "%Y-%m-%d")

        return html.Div(
            [
                html.H3(f'Первое сообщение    - {min_date}'),
                html.H3(f'Последнее сообщение - {max_date}'),
                html.Div(words_frequency_text),

                html.Div([
                    html.Div(children=[
                        html.H3(children='Всего сообщений'),
                        self.__generate_table(
                            df=self.messages_manipulator.get_message_count(),
                            columns=self.__get_columns())],
                    ),
                    # style={'display': 'inline-block'}),
                    html.Div(children=[
                        html.H3(children='В среднем за активный день'),
                        self.__generate_table(
                            df=self.messages_manipulator.get_mean_per_active_day(),
                            columns=self.__get_columns())],
                    ),
                    # style={'display': 'inline-block'}),
                    html.Div(children=[
                        html.H3(children='В среднем за год'),
                        self.__generate_table(
                            df=self.messages_manipulator.get_mean_per_active_year(),
                            columns=self.__get_columns())],
                    ),
                    html.Div(children=[
                        html.H3(children='В среднем за активный месяц'),
                        self.__generate_table(
                            df=self.messages_manipulator.get_mean_per_active_month(),
                            columns=self.__get_columns(additional=[
                                {
                                    'name': 'ГОД',
                                    'id': 'year',
                                    'type': 'numeric'
                                },
                            ]))],
                    ),
                    html.Div(children=[
                        html.H3(children='В среднем информативных слов'),
                        self.__generate_table(
                            df=self.messages_manipulator.get_mean_message_len(),
                            columns=self.__get_columns())],
                    ),
                ]),
                dcc.Loading(
                    [html.Div(id=ElementId.STATS_OUTPUT.value)],
                    type='circle',
                    color=choice(self.colors)
                ),
            ],
            # TODO: For now have unexpected errors https://github.com/plotly/dash/issues/1775
            # style=dict(display='flex', flexDirection='column', alignItems='center'),
        )

    def run(self) -> None:
        # TODO: Update report output when user choose another files dir
        self.app.run_server(self.host, self.port)
