# %%
import pandas as pd
import numpy as np
import chess
from seaborn.matrix import heatmap


# %%
class move_descriptors:
    def __init__(self, opening_key_loc="opening_dict.json") -> None:
        """Inits the class.

        Args:
            opening_key_loc (str, optional): Specifies location of the opening dictionary for opening parsing. Defaults to "opening_dict.json".
        """

        opening_key = pd.read_json(opening_key_loc)
        opening_key["list_moves"] = opening_key["clean_moves"].str.split(" ")
        self.opening_key = opening_key

    def first_move(self, moves: str):
        """Extracts the first move

        Args:
            moves (str): string of moves eg: "Nh3 d5 g3 e5"

        Returns:
            str: first move
        """
        return moves.split(" ")[0]

    def game_length(self, moves: str):
        """Calculates number of moves in game

        Args:
            moves (str): string of moves eg: "Nh3 d5 g3 e5"

        Returns:
            int: number of moves in game
        """
        return len(moves.split(" "))

    def sum_OO(self, moves: str):
        """Number of times king-side castling occurred in game

        Args:
            moves (str): string of moves eg: "Nh3 d5 g3 e5"

        Returns:
            int: number of times there was "O-O" within string
        """
        return moves.split(" ").count("O-O")

    def sum_OOO(self, moves: str):
        """Number of times queen-side castling occurred in game

        Args:
            moves (str): string of moves eg: "Nh3 d5 g3 e5"

        Returns:
            int: number of times there was "O-O-O" within string
        """
        return moves.split(" ").count("O-O-O")

    def both_castled(self, moves: str):
        """Have both players castled?

        Args:
            moves (str): string of moves eg: "Nh3 d5 g3 e5"

        Returns:
            bool: have both players castled
        """
        moves = moves.split(" ")
        castle_sum = 0
        castle_sum += moves.count("O-O-O")
        castle_sum += moves.count("O-O")
        if castle_sum == 2:
            return True
        else:
            return False

    def opposite_castle(self, moves: str):
        """Have players castled on opposite side of the board?

        Args:
            moves (str): string of moves eg: "Nh3 d5 g3 e5"

        Returns:
            bool: have both players castled on opposite side?
        """

        moves = moves.split(" ")
        queen_side = moves.count("O-O-O")
        king_side = moves.count("O-O")
        if queen_side == 1 and king_side == 1:
            return True
        else:
            return False

    def num_of_turns_queens_on_board(self, moves: str):
        """Number of turns queens are on board

        Args:
            moves (str): string of moves eg: "Nh3 d5 g3 e5"

        Returns:
            int: Number of turns queens are on board
        """
        board = chess.Board()
        moves = moves.split(" ")
        queen_list = np.zeros(len(moves), dtype=bool)
        for move_number, move in enumerate(moves):
            board.push_san(move)
            queen_zobrist = board.queens
            if queen_zobrist:
                queen_list[move_number] = True
            else:
                break
        np.where(queen_list == 0)
        return len(queen_list.nonzero()[0])

    def get_opening(self, moves):
        """Parses opening and returns descriptors based off them

        These include: ECO code, opening name, opening type (flank, closed ...etc), and opening moves

        Args:
            moves (str): string of moves eg: "Nh3 d5 g3 e5"

        Returns:
            pd.DataFrame: descriptors for ECO code, opening name, opening type, and opening moves
        """

        def is_move_same(openings, move, move_number):
            valid_openings = np.ones(len(openings), dtype=bool)
            for index, opening_moves in openings["list_moves"].iteritems():
                if len(opening_moves) > move_number:
                    if opening_moves[move_number] != move:
                        valid_openings[index] = 0
            return openings[valid_openings].reset_index(drop=True)

        moves = moves.split(" ")

        opening_key = self.opening_key

        potential_openings = opening_key.copy()

        for move_number, move in enumerate(moves):
            prev_len = len(potential_openings)
            potential_openings = is_move_same(potential_openings, move, move_number)
            curr_len = len(potential_openings)
            if prev_len == curr_len:
                break
            if curr_len == 0:
                break

        potential_openings["length_moves"] = potential_openings["list_moves"].apply(
            lambda m: len(m)
        )
        return potential_openings.loc[
            potential_openings["length_moves"].idxmax(),
            ["ECO code", "name", "type", "clean_moves"],
        ].rename(
            {
                "ECO code": "eco_code",
                "name": "opening_name",
                "type": "opening_type",
                "clean_moves": "opening_moves",
            }
        )


# %%
class heatmaps:
    BOARD_SIZE = 8

    def __init__(self, moves) -> None:
        self.moves = moves.split(" ")

    def board_to_array(board, pieces=None):
        """[summary]

        Args:
            board (chess.Board): chess.Board object.
            pieces (list, optional): Specify what pieces w.r.t. FEN definitions eg: ["P","k","K"]. Defaults to all pieces.

        Returns:
            np.array: returns 2D array of position
        """
        fen = board.fen().split(" ")[0]
        fen = fen.split("/")
        bs = heatmaps.BOARD_SIZE
        out_row = np.zeros(shape=(bs, bs), dtype=int)

        if not pieces:
            pieces = [
                "r",
                "n",
                "b",
                "q",
                "k",
                "b",
                "n",
                "r",
                "p",
                "R",
                "N",
                "B",
                "Q",
                "K",
                "B",
                "N",
                "R",
                "P",
            ]

        for row in range(bs):
            fen_row = fen[row]

            square_num = 0
            for letter in fen_row:
                if letter.isnumeric():
                    square_num += int(letter)
                elif letter in pieces:
                    out_row[row, square_num] = 1
                    square_num += 1
                else:
                    square_num += 1

        return out_row

    def move_array_board(self, pieces=None):
        """Calculates all the 2D position arrays for every move in a game

        Args:
            pieces (list, optional): Specify what pieces w.r.t. FEN definitions eg: ["P","k","K"]. Defaults to all pieces.

        Returns:
            np.array: returns 3D array of all positions in game
        """
        moves = self.moves
        bs = heatmaps.BOARD_SIZE
        # game = np.zeros(shape=bs)
        game = []
        board = chess.Board()
        for move_number, move in enumerate(moves):
            board.push_san(move)
            # game[move_number] = board_to_array(board,pieces = pieces)
            game.append(heatmaps.board_to_array(board, pieces=pieces))
        return np.dstack(game)

    def heatmap(self, pieces=None):
        arr = heatmap.move_array_board(pieces=pieces)
        AXIS = 2
        return arr.sum(axis=AXIS) / arr.shape[AXIS]


# %%
# import seaborn as sns
# dataset = pd.read_csv(R"demo_dataset.csv")
# out = dataset["moves"].apply(lambda moves: heatmaps(moves).heatmap(pieces=["P","p"]))
# sns.heatmap(np.mean(np.dstack(out.values),axis=2))
