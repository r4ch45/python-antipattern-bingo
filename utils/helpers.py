import pandas as pd
import numpy as np


def create_empty_board(k):
    board_length = int(k ** 0.5)
    df = pd.DataFrame(index=np.arange(0, k, 1))
    df["x"] = list(np.arange(0, board_length, 1)) * board_length
    df["y"] = sum([[i] * board_length for i in np.arange(0, board_length, 1)], [])
    df["xy"] = list(df.to_records(index=False))
    df["status"] = False
    return df


def points_to_board(points, k):
    board = create_empty_board(k)
    points["xy"] = list(points[["x", "y"]].to_records(index=False))
    board["status"] = (
        board["xy"].astype(str).isin(points["xy"].astype(str))
    )  # for some reason equality test on numpy record types is weird
    return board


def winner_check(board):
    status = any([n_in_row(board), n_in_col(board), n_in_diag(board)])
    return status


def n_in_row(board):
    k = len(board)
    board_length = int(k ** 0.5)

    status = False
    for i in np.arange(0, board_length, 1):
        if board[board["x"] == i]["status"].sum() == board_length:
            status = True
    return status


def n_in_col(board):
    k = len(board)
    board_length = int(k ** 0.5)

    status = False
    for i in np.arange(0, board_length, 1):
        if board[board["y"] == i]["status"].sum() == board_length:
            status = True
    return status


def n_in_diag(board):
    # https://stackoverflow.com/questions/45889231/how-to-check-for-3-in-a-row-in-tic-tac-toe-game
    k = len(board)
    board_length = int(k ** 0.5)

    statusforwards = (
        sum(
            [
                board[board["x"] == i][board["y"] == i]["status"].values
                for i in range(board_length)
            ]
        )
        == board_length
    )
    statusbackwards = (
        sum(
            [
                board[board["x"] == i][board["y"] == board_length - 1 - i]["status"].values
                for i in range(board_length)
            ]
        )
        == board_length
    )

    return any([statusforwards, statusbackwards])
