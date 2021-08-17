# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from utils.antipatterns import get_antipatterns_per_theme, pick_random_antipatterns
from utils.board import board


import numpy as np
import pandas as pd
import plotly.express as px
import textwrap


def customwrap(s, width=20):
    return "<br>".join(textwrap.wrap(s, width=width))


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Antipattern Bingo"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    id="intro-container",
                    children=[
                        html.H1(children=f"Python Anti-Pattern Bingo"),
                        dcc.Dropdown(
                            id="theme-dropdown",
                            multi=True,
                            placeholder="Select which topics to play with...",
                            style={"margin": "20px"},
                        ),
                        html.P("Select board size..."),
                        dcc.RadioItems(
                            id="board-size-radio",
                            options=[
                                {"label": str(i), "value": i} for i in [9, 16, 25]
                            ],
                            value=9,
                            labelStyle={"display": "inline-block", "marginTop": "5px"},
                        ),
                    ],
                    style={"margin": "20px"},
                ),
                html.Div(id="board-div", children=[dcc.Graph(id="board-scatter")]),
                html.Div(
                    id="item-info-container",
                    style={"margin": "20px", "width": "100%", "height": "300px"},
                ),
                dcc.Store(id="antipatterns-menu", data=get_antipatterns_per_theme()),
                dcc.Store(id="selected-antipatterns-menu"),
                dcc.Store(id="bingo-board-items"),
            ],
            className="page-main",
        )
    ],
    className="page-container",
    style={"width": "50%"},
)


@app.callback(Output("theme-dropdown", "options"), Input("antipatterns-menu", "data"))
def update_theme_options(patterns_per_theme):
    return [{"label": o, "value": o} for o in patterns_per_theme.keys()]


@app.callback(
    Output("selected-antipatterns-menu", "data"),
    Input("theme-dropdown", "value"),
    Input("antipatterns-menu", "data"),
)
def update_selected_antipatterns(selected_themes, patterns_per_theme):
    if (selected_themes is None) or (patterns_per_theme is None):
        return None
    else:
        return {your_key: patterns_per_theme[your_key] for your_key in selected_themes}


@app.callback(
    Output("bingo-board-items", "data"),
    Input("selected-antipatterns-menu", "data"),
    Input("board-size-radio", "value"),
)
def show_selected_antipatterns(selected_patterns_per_theme, k):
    if (selected_patterns_per_theme is None) or (k is None):
        return None
    else:
        return pick_random_antipatterns(selected_patterns_per_theme, n=k)


@app.callback(
    Output("board-scatter", "figure"),
    Input("bingo-board-items", "data"),
    Input("board-size-radio", "value"),
)
def make_board(board_items, k):

    if board_items is None:
        board_items = [None] * k
        formatted_board_items = board_items
    elif len(board_items) != k:
        board_items = [None] * k
        formatted_board_items = board_items
    else:
        board_items = [boarditem.replace(".rst", "") for boarditem in board_items]
        formatted_board_items = [
            customwrap(boarditem.replace("_", " ")) for boarditem in board_items
        ]

    board_length = int(k ** 0.5)

    x = list(np.arange(0, board_length, 1)) * board_length
    y = sum([[i] * board_length for i in np.arange(0, board_length, 1)], [])
    df = pd.DataFrame(
        {"x": x, "y": y, "names": formatted_board_items, "items": board_items}
    )

    fig = px.scatter(
        df, x="x", y="y", text="names", size=[50] * k, custom_data=["items"]
    )
    fig.update_layout(
        yaxis_range=[-1, board_length],
        xaxis_range=[-1, board_length],
        yaxis={"visible": False, "showticklabels": False},
        xaxis={"visible": False, "showticklabels": False},
        clickmode="event+select",
        autosize=False,
    )

    return fig


@app.callback(
    Output("item-info-container", "children"),
    Input("board-scatter", "hoverData"),
    Input("selected-antipatterns-menu", "data"),
)
def get_item_info(hover_data, selected_patterns_per_theme):

    if (selected_patterns_per_theme is None) or (hover_data is None):
        return {}

    theme = "readability"
    name = hover_data["points"][0]["customdata"][0]

    if name is None:
        return {}

    return html.Iframe(
        src=f"https://quantifiedcode.github.io/python-anti-patterns/{theme}/{name}.html",
        style={"width": "100%", "height": "100%"},
    )


if __name__ == "__main__":
    app.run_server(debug=True)
