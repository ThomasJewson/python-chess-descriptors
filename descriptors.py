# %%
import pandas as pd
import numpy as np
import chess


# %%
class move_descriptors:
    def __init__(self, opening_key_loc="opening_dict.json") -> None:

        opening_key = pd.read_json(opening_key_loc)
        opening_key["list_moves"] = opening_key["clean_moves"].str.split(" ")
        self.opening_key = opening_key

    def first_move(self, moves):
        return moves.split(" ")[0]

    def game_length(self, moves):
        return len(moves.split(" "))

    def sum_OO(self, moves):
        return moves.split(" ").count("O-O")

    def sum_OOO(self, moves):
        return moves.split(" ").count("O-O-O")

    def both_castled(self, moves):
        moves = moves.split(" ")
        castle_sum = 0
        castle_sum += moves.count("O-O-O")
        castle_sum += moves.count("O-O-O")
        if castle_sum == 2:
            return True
        else:
            return False

    def opposite_castle(self, moves):
        moves = moves.split(" ")
        black_side = moves.count("O-O-O")
        white_side = moves.count("O-O-O")
        if black_side == 1 and white_side == 1:
            return True
        else:
            return False

    def num_of_turns_queens_on_board(self, moves):
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
# dataset = pd.read_csv(R"demo_dataset.csv")

# mv = move_descriptors()
# dataset["moves"].apply(lambda moves: mv.get_opening(moves))
