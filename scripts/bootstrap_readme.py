#!/usr/bin/env python3
"""Regenerate README chess sections with correct repo issue links."""

import os
import sys

import chess
import chess.pgn
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import src.markdown as markdown
from main import get_game_owner

REPO = "taranggg/taranggg"


def normalize_last_moves(settings):
    """Ensure Start game is always credited to the configured game owner."""
    owner = get_game_owner(settings)
    path = "data/last_moves.txt"
    if not os.path.exists(path):
        return

    with open(path, "r") as file:
        lines = file.readlines()

    with open(path, "w") as file:
        for line in lines:
            if line.lower().startswith("start game:"):
                file.write(f"Start game: {owner}\n")
            else:
                file.write(line)


def replace_text_between(original_text, marker, replacement_text):
    delimiter_a = marker["begin"]
    delimiter_b = marker["end"]

    if original_text.find(delimiter_a) == -1 or original_text.find(delimiter_b) == -1:
        return original_text

    leading_text = original_text.split(delimiter_a)[0]
    trailing_text = original_text.split(delimiter_b)[1]

    return leading_text + delimiter_a + replacement_text + delimiter_b + trailing_text


def load_board():
    with open("games/current.pgn") as pgn_file:
        game = chess.pgn.read_game(pgn_file)
        board = game.board()

    for move in game.mainline_moves():
        board.push(move)

    return board


def main():
    os.environ["GITHUB_REPOSITORY"] = REPO

    with open("data/settings.yaml", "r") as settings_file:
        settings = yaml.load(settings_file, Loader=yaml.FullLoader)

    normalize_last_moves(settings)
    board = load_board()

    with open("README.md", "r") as file:
        readme = file.read()
        readme = replace_text_between(readme, settings["markers"]["board"], "{chess_board}")
        readme = replace_text_between(readme, settings["markers"]["moves"], "{moves_list}")
        readme = replace_text_between(readme, settings["markers"]["turn"], "{turn}")
        readme = replace_text_between(readme, settings["markers"]["last_moves"], "{last_moves}")
        readme = replace_text_between(readme, settings["markers"]["top_moves"], "{top_moves}")

    with open("README.md", "w") as file:
        file.write(
            readme.format(
                chess_board=markdown.board_to_markdown(board),
                moves_list=markdown.generate_moves_list(board),
                turn="white" if board.turn == chess.WHITE else "black",
                last_moves=markdown.generate_last_moves(),
                top_moves=markdown.generate_top_moves(),
            )
        )

    print(f"README updated for {REPO}")


if __name__ == "__main__":
    main()
