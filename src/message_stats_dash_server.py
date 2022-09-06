import logging
from enum import Enum
from random import choice

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

COLORS_SEQUENTIALS = [
    px.colors.sequential.Viridis,
    px.colors.sequential.GnBu,
    px.colors.sequential.deep,
    px.colors.sequential.dense,
]


class ElementId(Enum):
    STATS_OUTPUT = 'stats-output'


class MessageStatsDashServer:
    class ColumnName(Enum):
        DATE = 'date'
        TEXT = 'text'
        NAME = 'name'

    def __init__(self,
                 logger: logging.Logger,
                 messages: pd.DataFrame) -> None:
        # TODO: Add some assets files if needed
        self.app = Dash(__name__, assets_folder='./assets')

        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('parse').setLevel(logging.WARNING)
        self.app.logger = logger

        self.messages = messages

        self.host = 'localhost'
        self.port = 3838

        self.app.title = '[write-me] Stats'
        self.colors = choice(COLORS_SEQUENTIALS)
        self.app.layout = self.__get_layout()

    def __get_layout(self) -> html.Div:
        """Get layout loading spinner & stats output"""
        return html.Div(
            [
                html.H3('I have no idea why this page is empty'),
                dcc.Loading(
                    [html.Div(id=ElementId.STATS_OUTPUT.value)],
                    type='circle',
                    color=choice(self.colors)
                ),
            ],
            style=dict(display='flex', flexDirection='column', alignItems='center'),
        )

    def run(self) -> None:
        # TODO: Update report output when user choose another files dir
        self.app.run_server(self.host, self.port)