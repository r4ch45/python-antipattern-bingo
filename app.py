# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from sys import intern
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from utils.antipatterns import (
    get_antipatterns_df,
    wrangle_antipatterns_df,
    theme_colors,
)
from utils.helpers import points_to_board, winner_check

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
                        html.Div(
                            id="intro",
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
                                        {"label": str(i), "value": i}
                                        for i in [9, 16, 25]
                                    ],
                                    value=9,
                                    labelStyle={
                                        "display": "inline-block",
                                        "marginTop": "5px",
                                    },
                                ),
                                html.Button("New Board", id="new-board-button"),
                                html.Div(id="board-status"),
                            ],
                            className="six columns",
                        ),
                    ],
                    style={"width": "100%", "height": "25vh"},
                    className="row",
                ),
                html.Div(
                    id="board-container",
                    children=[
                        html.Div(
                            id="board-div",
                            children=[
                                dcc.Graph(id="board-scatter",
                                style={"height": "100%"},
                                responsive=True)
                            ],
                            style={
                                "height": "100%",
                            },
                            className="six columns",
                        ),
                        html.Div(
                            id="item-info-container",
                            style={
                                "height": "100%",
                            },
                            className="six columns",
                        ),
                    ],
                    style={"width": "100%", "height": "75vh"},
                    className="row",
                ),
                dcc.ConfirmDialog(id="bingo-box", message="BINGO!!!",),
                dcc.Store(
                    id="antipatterns-menu",
                    storage_type="session",
                    data=wrangle_antipatterns_df(get_antipatterns_df()).to_json(
                        orient="split"
                    ),
                ),
                dcc.Store(id="selected-antipatterns-menu", storage_type="session"),
                dcc.Store(id="bingo-board-items", storage_type="session"),
            ],
            style={"width": "100%", "height": "100vh"},
        )
    ],
    className="page-container",
    style={"width": "100%", "height": "100vh"},
)


@app.callback(Output("theme-dropdown", "options"),Output("theme-dropdown", "value"), Input("antipatterns-menu", "data"))
def update_theme_options(origjsondf):
    unique_themes = pd.read_json(origjsondf, orient="split")["theme"].unique()
    return [{"label": o, "value": o} for o in unique_themes], unique_themes


@app.callback(
    Output("selected-antipatterns-menu", "data"),
    Input("theme-dropdown", "value"),
    Input("antipatterns-menu", "data"),
)
def update_selected_antipatterns(selected_themes, origjsondff):
    origdff = pd.read_json(origjsondff, orient="split")
    if (selected_themes is None) or (origdff is None):
        return None
    else:
        return origdff[origdff["theme"].isin(selected_themes)].to_json(orient="split")


@app.callback(
    Output("bingo-board-items", "data"),
    Input("selected-antipatterns-menu", "data"),
    Input("board-size-radio", "value"),
    Input("new-board-button", "n_clicks"),
)
def create_board_antipatterns(selected_jsondf, k, clicks):
    if (selected_jsondf is None) or (k is None):
        return None
    else:
        selected_dff = pd.read_json(selected_jsondf, orient="split")
        if k <= len(selected_dff):
            return selected_dff.sample(k).to_json(orient="split")
        else:
            return None

@app.callback(
    Output("board-container", "hidden"),
    Output("board-status", "children"),
    Input("bingo-board-items", "data"),
    Input("board-size-radio", "value"),
)
def hide_graph(board_items_jsondf, k):
    message = html.P("More items needed to create board, try adding another theme.")
    if board_items_jsondf is None:
        return True, message

    elif len(board_items_jsondf)<k:
        return True, message
    else:
        return False, {}

@app.callback(
    Output("board-scatter", "figure"),
    Input("bingo-board-items", "data"),
    Input("board-size-radio", "value"),
)
def make_board(board_items_jsondf, k):

    if board_items_jsondf is None:
        return {}

    elif len(board_items_jsondf)<k:
        return {}
    else:
        df = pd.read_json(board_items_jsondf, orient="split")

    board_length = int(k ** 0.5)

    df["x"] = list(np.arange(0, board_length, 1)) * board_length
    df["y"] = sum([[i] * board_length for i in np.arange(0, board_length, 1)], [])

    fig = go.Figure(data=[], layout=go.Layout())

    for theme in df["theme"].unique():
        df_theme = df[df["theme"] == theme]
        fig.add_trace(
            go.Scatter(
                x=df_theme["x"],
                y=df_theme["y"],
                # marker_color=[theme_colors[theme]]*k,
                text=df_theme["readable_pattern"],
                textposition="middle center",
                customdata=df_theme["internet_path"],
                name=theme,
                marker={"color": theme_colors[theme], "size": 50, "symbol": "square"},
                selected={"marker": {"color": "darkgreen"}, "textfont" : {"color" : "limegreen"}},
                unselected={"marker": {"opacity": 0.9}, "textfont" : {"color" : "black"}},
                mode="markers+text",
            )
        )

    fig.update_layout(
        yaxis_range=[-1, board_length],
        xaxis_range=[-1, board_length],
        yaxis={"visible": False, "showticklabels": False},
        xaxis={"visible": False, "showticklabels": False},
        clickmode="event+select",
        autosize=True,
        legend_title_text="Theme",
        showlegend=True,
        # width=1200,
        # height=1200,
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

    if hover_data["points"][0]["customdata"] is None:
        return {}

    internet_path = hover_data["points"][0]["customdata"]

    if (internet_path is None) or (internet_path == "None"):
        return {}

    return html.Iframe(src=internet_path, style={"width": "100%", "height": "100%"},)


@app.callback(Output('bingo-box', 'displayed'),
    Input("board-scatter", "selectedData"),
    Input("board-size-radio", "value"),)
def have_you_won(selecteddata, boardsize):
    if selecteddata is None:
        return False
    points = pd.DataFrame(selecteddata["points"])
    board = points_to_board(points, boardsize)

    if winner_check(board):
        return True
    else:
        return False

if __name__ == "__main__":
    app.run_server(debug=True)
