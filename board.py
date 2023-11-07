import numpy as np

class Board():
    

    PIECE_TO_NUMBER = {'K':6,
                        'k':-6,
                        'Q':5,
                        'q':-5,
                        'R':4,
                        'r':-4,
                        'B':3,
                        'b':-3,
                        'N':2,
                        'n':-2,
                        'P':1,
                        'p':-1,
                        '.':0}
    NUMBER_TO_PIECE = {v:k for k,v in PIECE_TO_NUMBER.items()}

    def initialize_chessboard():
        self.board  = np.zeros((8,8), dtype = np.int8)

    # Function to set up the chessboard from a FEN string
    def set_up_chessboard(fen_string):
        chessboard = initialize_chessboard()
        rank, file = 0, 0

        for char in fen_string:
            if char == ' ':
                break
            if char == '/':
                rank += 1
                file = 0
            elif char.isdigit():
                file += int(char)
            else:
                chessboard[7 - rank][file] = PIECE_TO_NUMBER.get(char)
                file += 1

        return chessboard

    # Function to display the chessboard
    def display_chessboard(board, whites_perspective=True):
        if whites_perspective:
            for row in board:
                print(" ".join([NUMBER_TO_PIECE.get(p,p) for p in row]))
        else:
            for row in np.rot90(board, 2):
                print(" ".join([NUMBER_TO_PIECE.get(p,p) for p in row]))





chessboard = set_up_chessboard("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
display_chessboard(chessboard,0)





