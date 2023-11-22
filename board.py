
import numpy as np
import re

class Board():

    PIECE_TO_NUMBER = {'K':6, 'k':-6, 'Q':5,'q':-5, 'R':4,'r':-4,'B':3,'b':-3, 'N':2,'n':-2,'P':1,'p':-1,'.':0}
    NUMBER_TO_PIECE = {v:k for k,v in PIECE_TO_NUMBER.items()}
    NUMBER_TO_PIECE_EMOJI = {6: '♚', -6: '♔', 5: '♛', -5: '♕', 4: '♜', -4: '♖', 3: '♝', -3: '♗', 2: '♞', -2: '♘', 1: '♟', -1: '♙', 0: '.'}
    pks = PIECE_TO_NUMBER.keys()
    
    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
   
    WHITE_KING_CASTLE = 0b1
    WHITE_QUEEN_CASTLE = 0b10
    BLACK_KING_CASTLE = 0b100
    BLACK_QUEEN_CASTLE = 0b1000

    FILE_BITBOARDS = [0x0101010101010101,
                      0x0202020202020202,
                      0x0404040404040404,
                      0x0808080808080808,
                      0x1010101010101010,
                      0x2020202020202020,
                      0x4040404040404040,
                      0x8080808080808080]
    RANK_BITBOARDS = [0x00000000000000FF,
                   0x000000000000FF00,
                   0x0000000000FF0000,
                   0x00000000FF000000,
                   0x000000FF00000000,
                   0x0000FF0000000000,
                   0x00FF000000000000,
                   0xFF00000000000000
                   ]

    def __init__(self, fen = None):
        self.board  = np.zeros((8,8), dtype = np.int8)
        self.result= -1
        if not fen:
            fen = Board.STARTING_FEN
        self.last_fen = None
        self.init_fen = fen
        self.set_up_chessboard(fen)


    

    def set_up_chessboard(self, fen_string):
        rank, file = 0, 0
        fen_string = fen_string.split(" ")
        for char in fen_string[0]:
            if char == ' ':
                break
            if char == '/':
                rank += 1
                file = 0
            elif char.isdigit():
                file += int(char)
            else:
                self.board[7 - rank][file] = Board.PIECE_TO_NUMBER.get(char)
                file += 1
        if fen_string[1]:
            if fen_string[1][0] == 'b' or fen_string[1][0] == 'B':
                self.whites_move = 0
            else:
                self.whites_move = 1
        if fen_string[2]:
            self.castling_rights = 0b0
            if 'K' in fen_string[2]:
                self.castling_rights |= Board.WHITE_KING_CASTLE
            if 'Q' in fen_string[2]:
                self.castling_rights |= Board.WHITE_QUEEN_CASTLE
            if 'k' in fen_string[2]:
                self.castling_rights |= Board.BLACK_KING_CASTLE
            if 'q' in fen_string[2]:
                self.castling_rights |= Board.BLACK_QUEEN_CASTLE

        if fen_string[3]:
            if fen_string[3][0] != '-':
                self.en_passant_square = self.alphanum_to_coordinate(fen_string[3])
            else:
                self.en_passant_square = None
        if fen_string[4]:
            self.halfmove_clock = int(fen_string[4])
        if fen_string[5]:
            self.move_number= int(fen_string[5])
        self.update_bitboards()
        return self.board

    def export_fen(self):
        fen_parts = []

        for rank in range(7, -1, -1):
            empty_squares = 0
            for file in range(8):
                piece = self.board[rank][file]
                if piece == 0:
                    empty_squares += 1
                else:
                    if empty_squares > 0:
                        fen_parts.append(str(empty_squares))
                        empty_squares = 0
                    fen_parts.append(Board.NUMBER_TO_PIECE.get(piece))

            if empty_squares > 0:
                fen_parts.append(str(empty_squares))

            if rank > 0:
                fen_parts.append('/')
        fen_parts = [''.join(fen_parts)]
        # Players Turn
        fen_parts.append('w' if self.whites_move else 'b')
        # Castling
        castling_rights_str = ''
        if self.castling_rights & Board.WHITE_KING_CASTLE:
            castling_rights_str += 'K'
        if self.castling_rights & Board.WHITE_QUEEN_CASTLE:
            castling_rights_str += 'Q'
        if self.castling_rights & Board.BLACK_KING_CASTLE:
            castling_rights_str += 'k'
        if self.castling_rights & Board.BLACK_QUEEN_CASTLE:
            castling_rights_str += 'q'

        fen_parts.append(castling_rights_str or '-')

        # En passant square
        fen_parts.append(
            self.coordinate_to_alphanum(self.en_passant_square) if self.en_passant_square else '-'
        )

        # Halfmove clock
        fen_parts.append(str(self.halfmove_clock))

        # Move number
        fen_parts.append(str(self.move_number))

        return ' '.join(fen_parts).strip()


    def update_bitboards(self):
        self.bb_white_pawns = int(((self.board == 1).flatten() << np.arange(64,dtype=np.uint64)).sum())
        self.bb_black_pawns = int(((self.board == -1).flatten() << np.arange(64,dtype=np.uint64)).sum())
        self.bb_white_knights = int(((self.board == 2).flatten() << np.arange(64,dtype=np.uint64)).sum())
        self.bb_black_knights = int(((self.board == -2).flatten() << np.arange(64, dtype=np.uint64)).sum())
        self.bb_white_bishops = int(((self.board == 3).flatten() << np.arange(64, dtype=np.uint64)).sum())
        self.bb_black_bishops = int(((self.board == -3).flatten() << np.arange(64,dtype=np.uint64)).sum())
        self.bb_white_rooks = int(((self.board == 4).flatten() << np.arange(64,dtype=np.uint64)).sum())
        self.bb_black_rooks = int(((self.board == -4).flatten() << np.arange(64,dtype=np.uint64)).sum())
        self.bb_white_queens = int(((self.board == 5).flatten() << np.arange(64,dtype=np.uint64)).sum())
        self.bb_black_queens = int(((self.board == -5).flatten() << np.arange(64,dtype=np.uint64)).sum())
        self.bb_white_king = int(((self.board == 6).flatten() << np.arange(64,dtype=np.uint64)).sum())
        self.bb_black_king = int(((self.board == -6).flatten() << np.arange(64,dtype=np.uint64)).sum())
        self.bb_white_occupy = self.bb_white_pawns | self.bb_white_knights | self.bb_white_bishops | self.bb_white_rooks | self.bb_white_queens | self.bb_white_king
        self.bb_black_occupy = self.bb_black_pawns | self.bb_black_knights | self.bb_black_bishops | self.bb_black_rooks | self.bb_black_queens | self.bb_black_king
        self.bb_occupy = self.bb_white_occupy | self.bb_black_occupy

    def alphanum_to_coordinate(self, square):
        return (ord(square[0]) - ord('a'), int(square[1])-1)

    def coordinate_to_alphanum(self, coordinate):
        return f"{chr(ord('a') + coordinate[0])}{coordinate[1]+1}"

    def coordinate_to_bitboard(self,coord):
        if coord:
            return 2**( coord[0] + coord[1]*8)
        return 0

    def bitboard_to_coordinate(self, bitboard):
        if bitboard:
            square = bin(bitboard).count('0') - 1
            return square % 8, square // 8
        return None

    
    def move_pawn(self, from_bb, to_bb, promote=None):
        
        from_coord = self.bitboard_to_coordinate(from_bb)
        to_coord = self.bitboard_to_coordinate(to_bb)
        if self.coordinate_to_bitboard(self.en_passant_square) == to_bb:
            if self.whites_move: 
                self.board[to_coord[1]-1][to_coord[0]] = 0
            else:
                self.board[to_coord[1]+1][to_coord[0]] = 0
                
        if not promote:
            self.board[to_coord[1]][to_coord[0]] = self.board[from_coord[1]][from_coord[0]]
        else:
            promote = promote.lower() if not self.whites_move else promote
            self.board[to_coord[1]][to_coord[0]] = Board.PIECE_TO_NUMBER[promote]

            if self.whites_move:
                if to_coord == (0,7):
                    self.castling_rights &= ~self.BLACK_QUEEN_CASTLE
                if to_coord == (7,7):
                    self.castling_rights &= ~self.BLACK_KING_CASTLE
            else:
                if to_coord == (0,0):
                    self.castling_rights &= ~self.WHITE_QUEEN_CASTLE
                if to_coord == (7,0):
                    self.castling_rights &= ~self.WHITE_KING_CASTLE

        self.board[from_coord[1]][from_coord[0]] = 0
        
        double_move = from_bb << 16 == to_bb or from_bb >> 16 == to_bb
        if double_move:
            self.en_passant_square = (from_coord[0], (from_coord[1]+to_coord[1])//2)
        else:
            self.en_passant_square = None
        if not self.whites_move:
            self.move_number+=1
        self.halfmove_clock = 0
        self.whites_move = not self.whites_move 
        self.update_bitboards()

    def separate_bitboards(self, bitboard):
        set_bits = []
        while bitboard:
            position = (bitboard & -bitboard).bit_length() - 1
            set_bitboard = 1 << position
            set_bits.append(set_bitboard)
            bitboard &= bitboard - 1
        return set_bits

    def amb_from(self, from_bbs, to_bb):
        if bin(from_bbs).count("1")<=1:
            return from_bbs
        org_board = self.board.copy()
        to_coord = self.bitboard_to_coordinate(to_bb)
        correct_from_bb = []
        for from_bb in self.separate_bitboards(from_bbs):
            self.board = org_board.copy()
            from_coord = self.bitboard_to_coordinate(from_bb)
            self.board[to_coord[1]][to_coord[0]] = self.board[from_coord[1]][from_coord[0]]
            self.board[from_coord[1]][from_coord[0]] = 0
            self.update_bitboards()
            if not self.is_king_in_check(self.whites_move):
                correct_from_bb.append(from_bb)
        if len(correct_from_bb) != 1:
            print("AHHHHHHHHH")
        self.board = org_board
        self.update_bitboards()
        return correct_from_bb[0]
    


    def move_piece(self, from_bb, to_bb):
        if bin(from_bb).count("1")>1:
            from_bb = self.amb_from(from_bb, to_bb)
        from_coord = self.bitboard_to_coordinate(from_bb)
        to_coord = self.bitboard_to_coordinate(to_bb)
        if self.board[to_coord[1]][to_coord[0]]:
            if self.whites_move:
                if to_coord == (0,7):
                    self.castling_rights &= ~self.BLACK_QUEEN_CASTLE
                if to_coord == (7,7):
                    self.castling_rights &= ~self.BLACK_KING_CASTLE
            else:
                if to_coord == (0,0):
                    self.castling_rights &= ~self.WHITE_QUEEN_CASTLE
                if to_coord == (7,0):
                    self.castling_rights &= ~self.WHITE_KING_CASTLE
            self.halfmove_clock = 0
        self.board[to_coord[1]][to_coord[0]] = self.board[from_coord[1]][from_coord[0]]
        self.board[from_coord[1]][from_coord[0]] = 0
        
        if not self.whites_move:
            self.move_number+=1
        self.whites_move = not self.whites_move
        self.en_passant_square = None
        self.update_bitboards()

    def move_rook(self, from_bb, to_bb):
        if bin(from_bb).count("1")>1:
            from_bb = self.amb_from(from_bb, to_bb)
        if self.whites_move:
            if from_bb == 0x0000000000000080:
                self.castling_rights &= ~self.WHITE_KING_CASTLE
            elif from_bb == 0x0000000000000001:
                self.castling_rights &= ~self.WHITE_QUEEN_CASTLE
        else:
            if from_bb == 0x8000000000000000:
                self.castling_rights &= ~self.BLACK_KING_CASTLE
            elif from_bb == 0x0100000000000000:
                self.castling_rights &= ~self.BLACK_QUEEN_CASTLE
        return self.move_piece(from_bb,to_bb)
    def move_king(self, from_bb, to_bb):
        if self.whites_move:
            self.castling_rights &= ~self.WHITE_KING_CASTLE
            self.castling_rights &= ~self.WHITE_QUEEN_CASTLE
        else:
            self.castling_rights &= ~self.BLACK_KING_CASTLE        
            self.castling_rights &= ~self.BLACK_QUEEN_CASTLE
        return self.move_piece(from_bb,to_bb)

    def move_castle(self, from_bb, to_bb):
        if self.whites_move:
            self.castling_rights &= ~self.WHITE_KING_CASTLE
            self.castling_rights &= ~self.WHITE_QUEEN_CASTLE
            if to_bb == 0x0000000000000040: # King-side castling
                self.board[0][5],self.board[0][7] = self.board[0][7],0             
            else:
                self.board[0][3],self.board[0][0] = self.board[0][0],0
            self.move_piece(from_bb, to_bb)
        else:
            self.castling_rights &= ~self.BLACK_KING_CASTLE        
            self.castling_rights &= ~self.BLACK_QUEEN_CASTLE
            if to_bb == 0x4000000000000000: # King-side castling
                self.board[7][5],self.board[7][7] = self.board[7][7],0
            else:
                self.board[7][3],self.board[7][0] = self.board[7][0],0
            self.move_piece(from_bb, to_bb)

    def make_algebraic_move(self, move):
        temp_fen = self.export_fen()
        if move[0] in ('a','b','c','d','e','f','g','h'):
            file = ord(move[0]) - ord('a')
            if '=' in move:
                promote_peice = move.split('=')[1][0]
            else:
               promote_peice=None
            if move [1] == 'x':
                to_square = self.alphanum_to_coordinate(move[2:4])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard = Board.FILE_BITBOARDS[file] & self.from_pawn_attacks(to_square_bitboard,self.whites_move) & self.bb_white_pawns
                    to_square_bitboard &= self.bb_black_occupy | self.coordinate_to_bitboard(self.en_passant_square)
                else:
                    from_square_bitboard = Board.FILE_BITBOARDS[file] & self.from_pawn_attacks(to_square_bitboard,self.whites_move) & self.bb_black_pawns
                    to_square_bitboard &= self.bb_white_occupy | self.coordinate_to_bitboard(self.en_passant_square)
            else:
                to_square = self.alphanum_to_coordinate(move[0:2])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard = Board.FILE_BITBOARDS[file] & self.from_pawn_move(to_square_bitboard,self.whites_move) & self.bb_white_pawns
                    to_square_bitboard &= ~self.bb_black_occupy
                else:
                    from_square_bitboard = Board.FILE_BITBOARDS[file] & self.from_pawn_move(to_square_bitboard,self.whites_move) & self.bb_black_pawns
                    to_square_bitboard &= ~self.bb_white_occupy

            if from_square_bitboard and to_square_bitboard:
                self.move_pawn(from_square_bitboard, to_square_bitboard, promote_peice)
            else:
                print("not valid")
                return -1

        elif move[0] == 'N':
            naked_move, _ = re.subn("[x+#]",'',move)
            if len(naked_move) == 3:
                to_square = self.alphanum_to_coordinate(naked_move[1:3])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_knight_move(to_square_bitboard,self.whites_move) & self.bb_white_knights
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_knight_move(to_square_bitboard,self.whites_move) & self.bb_black_knights
                    #to_square_bitboard &= self.bb_white_occupy
                
            elif len(naked_move) == 4:
                to_square = self.alphanum_to_coordinate(naked_move[2:4])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_knight_move(to_square_bitboard,self.whites_move) & self.bb_white_knights
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_knight_move(to_square_bitboard,self.whites_move) & self.bb_black_knights
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')]
                

            elif len(naked_move) == 5:
                to_square = self.alphanum_to_coordinate(naked_move[3:5])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_knight_move(to_square_bitboard,self.whites_move) & self.bb_white_knights
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_knight_move(to_square_bitboard,self.whites_move) & self.bb_black_knights
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1] & Board.FILE_BITBOARDS[ord(naked_move[2])-ord('a')]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')] & Board.RANK_BITBOARDS[int(naked_move[2])-1]
            if from_square_bitboard and to_square_bitboard:
                self.move_piece(from_square_bitboard, to_square_bitboard)
            else:
                print("not valid")
                return -1

        elif move[0] == 'B':
            naked_move, _ = re.subn("[x+#]",'',move)
            if len(naked_move) == 3:
                to_square = self.alphanum_to_coordinate(naked_move[1:3])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_bishop_move(to_square_bitboard,self.whites_move) & self.bb_white_bishops
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_bishop_move(to_square_bitboard,self.whites_move) & self.bb_black_bishops
                    #to_square_bitboard &= self.bb_white_occupy
                
            elif len(naked_move) == 4:
                to_square = self.alphanum_to_coordinate(naked_move[2:4])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_bishop_move(to_square_bitboard,self.whites_move) & self.bb_white_bishops
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_bishop_move(to_square_bitboard,self.whites_move) & self.bb_black_bishops
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')]
                

            elif len(naked_move) == 5:
                to_square = self.alphanum_to_coordinate(naked_move[3:5])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_bishop_move(to_square_bitboard,self.whites_move) & self.bb_white_bishops
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_bishop_move(to_square_bitboard,self.whites_move) & self.bb_black_bishops
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1] & Board.FILE_BITBOARDS[ord(naked_move[2])-ord('a')]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')] & Board.RANK_BITBOARDS[int(naked_move[2])-1]
            if from_square_bitboard and to_square_bitboard:
                self.move_piece(from_square_bitboard, to_square_bitboard)
            else:
                print("not valid")
                return -1

        elif move[0] == 'R':
            naked_move, _ = re.subn("[x+#]",'',move)
            if len(naked_move) == 3:
                to_square = self.alphanum_to_coordinate(naked_move[1:3])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_rook_move(to_square_bitboard,self.whites_move) & self.bb_white_rooks
                    
                else:
                    from_square_bitboard =  self.from_rook_move(to_square_bitboard,self.whites_move) & self.bb_black_rooks
                    
                
            elif len(naked_move) == 4:
                to_square = self.alphanum_to_coordinate(naked_move[2:4])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_rook_move(to_square_bitboard,self.whites_move) & self.bb_white_rooks
                    
                else:
                    from_square_bitboard = self.from_rook_move(to_square_bitboard,self.whites_move) & self.bb_black_rooks
                    
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')]
                

            elif len(naked_move) == 5:
                to_square = self.alphanum_to_coordinate(naked_move[3:5])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_rook_move(to_square_bitboard,self.whites_move) & self.bb_white_rooks
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_rook_move(to_square_bitboard,self.whites_move) & self.bb_black_rooks
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1] & Board.FILE_BITBOARDS[ord(naked_move[2])-ord('a')]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')] & Board.RANK_BITBOARDS[int(naked_move[2])-1]
            if from_square_bitboard and to_square_bitboard:
                self.move_rook(from_square_bitboard, to_square_bitboard)
            else:
                print("not valid")
                return -1

        elif move[0] == 'Q':
            naked_move, _ = re.subn("[x+#]",'',move)
            if len(naked_move) == 3:
                to_square = self.alphanum_to_coordinate(naked_move[1:3])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_queen_move(to_square_bitboard,self.whites_move) & self.bb_white_queens
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard = self.from_queen_move(to_square_bitboard,self.whites_move) & self.bb_black_queens
                    #to_square_bitboard &= self.bb_white_occupy
              
            elif len(naked_move) == 4:
                to_square = self.alphanum_to_coordinate(naked_move[2:4])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard = self.from_queen_move(to_square_bitboard,self.whites_move) & self.bb_white_queens
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard = self.from_queen_move(to_square_bitboard,self.whites_move) & self.bb_black_queens
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')]
                

            elif len(naked_move) == 5:
                to_square = self.alphanum_to_coordinate(naked_move[3:5])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard = self.from_queen_move(to_square_bitboard,self.whites_move) & self.bb_white_queens
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard = self.from_queen_move(to_square_bitboard,self.whites_move) & self.bb_black_queens
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1] & Board.FILE_BITBOARDS[ord(naked_move[2])-ord('a')]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')] & Board.RANK_BITBOARDS[int(naked_move[2])-1]
            if from_square_bitboard and to_square_bitboard:
                self.move_piece(from_square_bitboard, to_square_bitboard)
            else:
                print("not valid")
                return -1

        elif move[0] == 'K':
            naked_move, _ = re.subn("[x+#]",'',move)
            if len(naked_move) == 3:
                to_square = self.alphanum_to_coordinate(naked_move[1:3])
                to_square_bitboard = self.coordinate_to_bitboard(to_square) & self.king_moves(self.whites_move)
                if self.whites_move:
                    from_square_bitboard = self.bb_white_king
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard = self.bb_black_king
                    #to_square_bitboard &= self.bb_white_occupy
                if to_square_bitboard:
                    self.move_king(from_square_bitboard, to_square_bitboard)
                else:
                    print("not valid")
                    return -1
            else:
                print("AHHHHHHHH")
                return -1
        elif move[0].upper() == 'O' or move[0] == '0':

            if move.upper().startswith("O-O-O") or move.startswith("0-0-0"):
                if self.whites_move:
                    from_square_bitboard = self.bb_white_king
                    to_square_bitboard = 0x0000000000000004  # Queen-side castling
                else:
                    from_square_bitboard = self.bb_black_king
                    to_square_bitboard = 0x0400000000000000 
            elif move.upper().startswith("O-O") or move.startswith("0-0"):
                if self.whites_move:
                    from_square_bitboard = self.bb_white_king
                    to_square_bitboard = 0x0000000000000040  # King-side castling
                else:
                    from_square_bitboard = self.bb_black_king
                    to_square_bitboard = 0x4000000000000000
            if to_square_bitboard & self.king_moves(self.whites_move):
                self.move_castle(from_square_bitboard, to_square_bitboard)
            else:
                print("Not Valid")
                return -1
        else:
            print("Not Valid")
            return -1
        self.last_fen = temp_fen
        return self.export_fen()

    def get_to_from_square_algebraic_move(self, move, return_bitboard=True):
        
        if move[0] in ('a','b','c','d','e','f','g','h'):
            file = ord(move[0]) - ord('a')
            if '=' in move:
                promote_peice = move.split('=')[1][0]
            else:
               promote_peice=None
            if move [1] == 'x':
                to_square = self.alphanum_to_coordinate(move[2:4])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard = Board.FILE_BITBOARDS[file] & self.from_pawn_attacks(to_square_bitboard,self.whites_move) & self.bb_white_pawns
                    to_square_bitboard &= self.bb_black_occupy | self.coordinate_to_bitboard(self.en_passant_square)
                else:
                    from_square_bitboard = Board.FILE_BITBOARDS[file] & self.from_pawn_attacks(to_square_bitboard,self.whites_move) & self.bb_black_pawns
                    to_square_bitboard &= self.bb_white_occupy | self.coordinate_to_bitboard(self.en_passant_square)
            else:
                to_square = self.alphanum_to_coordinate(move[0:2])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard = Board.FILE_BITBOARDS[file] & self.from_pawn_move(to_square_bitboard,self.whites_move) & self.bb_white_pawns
                    to_square_bitboard &= ~self.bb_black_occupy
                else:
                    from_square_bitboard = Board.FILE_BITBOARDS[file] & self.from_pawn_move(to_square_bitboard,self.whites_move) & self.bb_black_pawns
                    to_square_bitboard &= ~self.bb_white_occupy

            if from_square_bitboard and to_square_bitboard:
                if return_bitboard:
                    return (from_square_bitboard, to_square_bitboard)
                return (self.bitboard_to_coordinate(from_square_bitboard), self.bitboard_to_coordinate(to_square_bitboard))
                    
            else:
                print("not valid")
                return -1

        elif move[0] == 'N':
            naked_move, _ = re.subn("[x+#]",'',move)
            if len(naked_move) == 3:
                to_square = self.alphanum_to_coordinate(naked_move[1:3])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_knight_move(to_square_bitboard,self.whites_move) & self.bb_white_knights
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_knight_move(to_square_bitboard,self.whites_move) & self.bb_black_knights
                    #to_square_bitboard &= self.bb_white_occupy
                
            elif len(naked_move) == 4:
                to_square = self.alphanum_to_coordinate(naked_move[2:4])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_knight_move(to_square_bitboard,self.whites_move) & self.bb_white_knights
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_knight_move(to_square_bitboard,self.whites_move) & self.bb_black_knights
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')]
                

            elif len(naked_move) == 5:
                to_square = self.alphanum_to_coordinate(naked_move[3:5])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_knight_move(to_square_bitboard,self.whites_move) & self.bb_white_knights
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_knight_move(to_square_bitboard,self.whites_move) & self.bb_black_knights
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1] & Board.FILE_BITBOARDS[ord(naked_move[2])-ord('a')]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')] & Board.RANK_BITBOARDS[int(naked_move[2])-1]
            if from_square_bitboard and to_square_bitboard:
                from_square_bitboard = self.amb_from(from_square_bitboard, to_square_bitboard)
                if return_bitboard:
                    return (from_square_bitboard, to_square_bitboard)
                return (self.bitboard_to_coordinate(from_square_bitboard), self.bitboard_to_coordinate(to_square_bitboard))
            else:
                print("not valid")
                return -1

        elif move[0] == 'B':
            naked_move, _ = re.subn("[x+#]",'',move)
            if len(naked_move) == 3:
                to_square = self.alphanum_to_coordinate(naked_move[1:3])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_bishop_move(to_square_bitboard,self.whites_move) & self.bb_white_bishops
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_bishop_move(to_square_bitboard,self.whites_move) & self.bb_black_bishops
                    #to_square_bitboard &= self.bb_white_occupy
                
            elif len(naked_move) == 4:
                to_square = self.alphanum_to_coordinate(naked_move[2:4])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_bishop_move(to_square_bitboard,self.whites_move) & self.bb_white_bishops
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_bishop_move(to_square_bitboard,self.whites_move) & self.bb_black_bishops
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')]
                

            elif len(naked_move) == 5:
                to_square = self.alphanum_to_coordinate(naked_move[3:5])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_bishop_move(to_square_bitboard,self.whites_move) & self.bb_white_bishops
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_bishop_move(to_square_bitboard,self.whites_move) & self.bb_black_bishops
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1] & Board.FILE_BITBOARDS[ord(naked_move[2])-ord('a')]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')] & Board.RANK_BITBOARDS[int(naked_move[2])-1]
            if from_square_bitboard and to_square_bitboard:
                from_square_bitboard = self.amb_from(from_square_bitboard, to_square_bitboard)
                if return_bitboard:
                    return (from_square_bitboard, to_square_bitboard)
                return (self.bitboard_to_coordinate(from_square_bitboard), self.bitboard_to_coordinate(to_square_bitboard))
            
            else:
                print("not valid")
                return -1

        elif move[0] == 'R':
            naked_move, _ = re.subn("[x+#]",'',move)
            if len(naked_move) == 3:
                to_square = self.alphanum_to_coordinate(naked_move[1:3])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_rook_move(to_square_bitboard,self.whites_move) & self.bb_white_rooks
                    
                else:
                    from_square_bitboard =  self.from_rook_move(to_square_bitboard,self.whites_move) & self.bb_black_rooks
                    
                
            elif len(naked_move) == 4:
                to_square = self.alphanum_to_coordinate(naked_move[2:4])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_rook_move(to_square_bitboard,self.whites_move) & self.bb_white_rooks
                    
                else:
                    from_square_bitboard = self.from_rook_move(to_square_bitboard,self.whites_move) & self.bb_black_rooks
                    
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')]
                

            elif len(naked_move) == 5:
                to_square = self.alphanum_to_coordinate(naked_move[3:5])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_rook_move(to_square_bitboard,self.whites_move) & self.bb_white_rooks
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard =  self.from_rook_move(to_square_bitboard,self.whites_move) & self.bb_black_rooks
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1] & Board.FILE_BITBOARDS[ord(naked_move[2])-ord('a')]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')] & Board.RANK_BITBOARDS[int(naked_move[2])-1]
            if from_square_bitboard and to_square_bitboard:
                from_square_bitboard = self.amb_from(from_square_bitboard, to_square_bitboard)
                if return_bitboard:
                    return (from_square_bitboard, to_square_bitboard)
                return (self.bitboard_to_coordinate(from_square_bitboard), self.bitboard_to_coordinate(to_square_bitboard))
            
            else:
                print("not valid")
                return -1

        elif move[0] == 'Q':
            naked_move, _ = re.subn("[x+#]",'',move)
            if len(naked_move) == 3:
                to_square = self.alphanum_to_coordinate(naked_move[1:3])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard =  self.from_queen_move(to_square_bitboard,self.whites_move) & self.bb_white_queens
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard = self.from_queen_move(to_square_bitboard,self.whites_move) & self.bb_black_queens
                    #to_square_bitboard &= self.bb_white_occupy
              
            elif len(naked_move) == 4:
                to_square = self.alphanum_to_coordinate(naked_move[2:4])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard = self.from_queen_move(to_square_bitboard,self.whites_move) & self.bb_white_queens
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard = self.from_queen_move(to_square_bitboard,self.whites_move) & self.bb_black_queens
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')]
                

            elif len(naked_move) == 5:
                to_square = self.alphanum_to_coordinate(naked_move[3:5])
                to_square_bitboard = self.coordinate_to_bitboard(to_square)
                if self.whites_move:
                    from_square_bitboard = self.from_queen_move(to_square_bitboard,self.whites_move) & self.bb_white_queens
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard = self.from_queen_move(to_square_bitboard,self.whites_move) & self.bb_black_queens
                    #to_square_bitboard &= self.bb_white_occupy
                if naked_move[1].isdigit():
                    from_square_bitboard&= Board.RANK_BITBOARDS[int(naked_move[1])-1] & Board.FILE_BITBOARDS[ord(naked_move[2])-ord('a')]
                else:
                    from_square_bitboard&= Board.FILE_BITBOARDS[ord(naked_move[1])-ord('a')] & Board.RANK_BITBOARDS[int(naked_move[2])-1]
            if from_square_bitboard and to_square_bitboard:
                from_square_bitboard = self.amb_from(from_square_bitboard, to_square_bitboard)
                if return_bitboard:
                    return (from_square_bitboard, to_square_bitboard)
                return (self.bitboard_to_coordinate(from_square_bitboard), self.bitboard_to_coordinate(to_square_bitboard))
            
            else:
                print("not valid")
                return -1

        elif move[0] == 'K':
            naked_move, _ = re.subn("[x+#]",'',move)
            if len(naked_move) == 3:
                to_square = self.alphanum_to_coordinate(naked_move[1:3])
                to_square_bitboard = self.coordinate_to_bitboard(to_square) & self.king_moves(self.whites_move)
                if self.whites_move:
                    from_square_bitboard = self.bb_white_king
                    #to_square_bitboard &= self.bb_black_occupy
                else:
                    from_square_bitboard = self.bb_black_king
                    #to_square_bitboard &= self.bb_white_occupy
                if to_square_bitboard:
                    return (self.bitboard_to_coordinate(from_square_bitboard), self.bitboard_to_coordinate(to_square_bitboard))
                else:
                    print("not valid")
                    return -1
            else:
                print("AHHHHHHHH")
                return -1
        elif move[0].upper() == 'O' or move[0] == '0':

            if move.upper().startswith("O-O-O") or move.startswith("0-0-0"):
                if self.whites_move:
                    from_square_bitboard = self.bb_white_king
                    to_square_bitboard = 0x0000000000000004  # Queen-side castling
                else:
                    from_square_bitboard = self.bb_black_king
                    to_square_bitboard = 0x0400000000000000 
            elif move.upper().startswith("O-O") or move.startswith("0-0"):
                if self.whites_move:
                    from_square_bitboard = self.bb_white_king
                    to_square_bitboard = 0x0000000000000040  # King-side castling
                else:
                    from_square_bitboard = self.bb_black_king
                    to_square_bitboard = 0x4000000000000000
            if to_square_bitboard & self.king_moves(self.whites_move):
                from_square_bitboard = self.amb_from(from_square_bitboard, to_square_bitboard)
                if return_bitboard:
                    return (from_square_bitboard, to_square_bitboard)
                return (self.bitboard_to_coordinate(from_square_bitboard), self.bitboard_to_coordinate(to_square_bitboard))
            
            else:
                print("Not Valid")
                return -1
        else:
            print("Not Valid")
            return -1
        


    def display_bitboards(self):
        print("White Pawn BitBoard:")
        self.display_bitboard(self.bb_white_pawns)
        print("-"*10)
        print("White Pawn Attack BitBoard:")
        self.display_bitboard(self.pawn_moves(white=True))
        print("-"*10)

        print("Black Pawn BitBoard:")
        self.display_bitboard(self.bb_black_pawns)

        print("-"*10)
        print("Black Pawn Attack BitBoard:")
        self.display_bitboard(self.pawn_moves(white = False))
        print("-"*10)

        print("White Knights BitBoard:")
        self.display_bitboard(self.bb_white_knights)
        print("-"*10)
        print("White Knights Attack BitBoard:")
        self.display_bitboard(self.knight_moves(white = True))
        print("-"*10)

        print("Black Knights BitBoard:")
        self.display_bitboard(self.bb_black_knights)
        print("-"*10)
        print("Black Knights Attack BitBoard:")
        self.display_bitboard(self.knight_moves(white = False))
        print("-"*10)

        print("White Bishops BitBoard:")
        self.display_bitboard(self.bb_white_bishops)
        print("-"*10)
        print("White Bishops Attack BitBoard:")
        self.display_bitboard(self.bishop_moves(white = True))
        print("-"*10)

        print("Black Bishops BitBoard:")
        self.display_bitboard(self.bb_black_bishops)
        print("-"*10)

        print("Black Bishops BitBoard:")
        self.display_bitboard(self.bishop_moves(white = False))
        print("-"*10)

        print("White Rooks BitBoard:")
        self.display_bitboard(self.bb_white_rooks)
        print("-"*10)

        print("White Rooks Attack BitBoard:")
        self.display_bitboard(self.rook_moves(white = True))
        print("-"*10)
        
        print("Black Rooks BitBoard:")
        self.display_bitboard(self.bb_black_rooks)
        print("-"*10)

        print("Black Rooks Attack BitBoard:")
        self.display_bitboard(self.rook_moves(white = False))
        print("-"*10)

        print("White Queen BitBoard:")
        self.display_bitboard(self.bb_white_queens)
        print("-"*10)
        print("White Queen Attack BitBoard:")
        self.display_bitboard(self.queen_moves(white = True))
        print("-"*10)

        print("Black Queen BitBoard:")
        self.display_bitboard(self.bb_black_queens)
        print("-"*10)

        print("Black Queen Attack BitBoard:")
        self.display_bitboard(self.queen_moves(white = False))
        print("-"*10)

        print("White King BitBoard:")
        self.display_bitboard(self.bb_white_king)
        print("-"*10)
        print("White King Attacks BitBoard:")
        self.display_bitboard(self.king_moves(white = True))
        print("-"*10)

        print("Black King BitBoard:")
        self.display_bitboard(self.bb_black_king)
        print("-"*10)
        print("Black King Attack BitBoard:")
        self.display_bitboard(self.king_moves(white = False))
        print("-"*10)

    def display_bitboard(self,bitboard):
        for rank in range(7, -1, -1):
            print(bin(bitboard >> (rank * 8) & 0xFF)[2:].zfill(8)[::-1])
    
    def pawn_attacks(self,white=True):

        attack_bitboard = 0
        if white:
            # Left attacks
            left_attacks = (self.bb_white_pawns & 0xFEFEFEFEFEFEFEFE) << 7
            attack_bitboard |= left_attacks

            # Right attacks
            right_attacks = (self.bb_white_pawns & 0x7F7F7F7F7F7F7F7F) << 9
            attack_bitboard |= right_attacks
            attack_bitboard &= self.bb_black_occupy
        else:
            # Left attacks
            left_attacks = (self.bb_black_pawns & 0xFEFEFEFEFEFEFEFE) >> 9
            attack_bitboard |= left_attacks

            # Right attacks
            right_attacks = (self.bb_black_pawns & 0x7F7F7F7F7F7F7F7F) >> 7
            attack_bitboard |= right_attacks
            attack_bitboard &= self.bb_white_occupy

        return attack_bitboard | self.coordinate_to_bitboard(self.en_passant_square)

    def from_pawn_attacks(self, position, white=True):

        attack_bitboard = 0
        if not white:
            # Left attacks
            left_attacks = (position & 0xFEFEFEFEFEFEFEFE) << 7
            attack_bitboard |= left_attacks 

            # Right attacks
            right_attacks = (position & 0x7F7F7F7F7F7F7F7F) << 9
            attack_bitboard |= right_attacks

            attack_bitboard &= (self.bb_black_occupy| self.coordinate_to_bitboard(self.en_passant_square))
        else:
            # Left attacks
            left_attacks = (position & 0xFEFEFEFEFEFEFEFE) >> 9
            attack_bitboard |= left_attacks

            # Right attacks
            right_attacks = (position & 0x7F7F7F7F7F7F7F7F) >> 7
            attack_bitboard |= right_attacks
            attack_bitboard &= (self.bb_white_occupy | self.coordinate_to_bitboard(self.en_passant_square))

        return attack_bitboard 

    def pawn_moves(self, white):
        attack_bitboard = 0
        if white:
            attack_bitboard |= ((self.bb_white_pawns & 0x000000000000FF00) << 8 ) & ~self.bb_occupy
            attack_bitboard |= (attack_bitboard << 8) & ~self.bb_occupy
            attack_bitboard |= ((self.bb_white_pawns & 0x00FFFFFFFFFF0000) << 8 ) & ~self.bb_occupy
        else:
            attack_bitboard |= ((self.bb_black_pawns & 0x00FF000000000000) >> 8 ) & ~self.bb_occupy
            attack_bitboard |= (attack_bitboard >> 8) & ~self.bb_occupy
            attack_bitboard |= ((self.bb_black_pawns & 0x0000FFFFFFFFFF00) >> 8 ) & ~self.bb_occupy

        return attack_bitboard|self.pawn_attacks(white)
    
    def from_pawn_move(self, position, white=True):
        from_bitboard = 0x00FFFFFFFFFFFF00
        if not white:
            from_bitboard &= (position << 8) & self.bb_black_pawns 
            if from_bitboard != 0:
                return from_bitboard
            from_bitboard = (position << 16) & self.bb_black_pawns & ~self.bb_occupy << 8
            return from_bitboard
        else:
            from_bitboard &= (position >> 8) & self.bb_white_pawns 
            if from_bitboard != 0:
                return from_bitboard
            from_bitboard = (position >> 16) & self.bb_white_pawns & (~self.bb_occupy >> 8)
            return from_bitboard

    def rook_moves(self, white, queen = False):
        # Initialize an empty bitboard for rook attacks
        attack_bitboard = 0
        if queen:
            rook_bitboard = self.bb_white_queens if white else self.bb_black_queens
        else:
            rook_bitboard = self.bb_white_rooks if white else self.bb_black_rooks
        self_occupy = self.bb_white_occupy if white else self.bb_black_occupy
        # Generate horizontal (rank) attacks
        left_attacks = rook_bitboard & 0xFEFEFEFEFEFEFEFE
        while left_attacks & 0xFEFEFEFEFEFEFEFE != 0:
            left_attacks >>= 1
            
            attack_bitboard |= left_attacks
            left_attacks &= ~self.bb_occupy

        # Generate horizontal (rank) attacks to the right
        right_attacks = rook_bitboard & 0x7F7F7F7F7F7F7F7F
        while right_attacks & 0x7F7F7F7F7F7F7F7F != 0:
            right_attacks <<= 1
            
            attack_bitboard |= right_attacks
            right_attacks &= ~self.bb_occupy

        # Generate vertical (file) attacks upward
        up_attacks = rook_bitboard & 0x00FFFFFFFFFFFFFF
        while up_attacks & 0x00FFFFFFFFFFFFFF != 0:
            up_attacks <<= 8
            
            attack_bitboard |= up_attacks
            up_attacks &= ~self.bb_occupy

        # Generate vertical (file) attacks downward
        down_attacks = rook_bitboard & 0xFFFFFFFFFFFFFF00
        while down_attacks & 0xFFFFFFFFFFFFFF00  != 0:
            down_attacks >>= 8
            
            attack_bitboard |= down_attacks
            down_attacks &= ~self.bb_occupy

        return attack_bitboard & ~self_occupy

    def from_rook_move(self, position, white, queen = False):
        # Initialize an empty bitboard for rook attacks
        attack_bitboard = 0
        if queen:
            rook_bitboard = self.bb_white_queens if white else self.bb_black_queens
        else:
            rook_bitboard = self.bb_white_rooks if white else self.bb_black_rooks
        # Generate horizontal (rank) attacks
        left_attacks = position & 0xFEFEFEFEFEFEFEFE
        while left_attacks & 0xFEFEFEFEFEFEFEFE != 0:
            left_attacks >>= 1
            
            attack_bitboard |= left_attacks
            left_attacks &= ~self.bb_occupy

        # Generate horizontal (rank) attacks to the right
        right_attacks = position & 0x7F7F7F7F7F7F7F7F
        while right_attacks & 0x7F7F7F7F7F7F7F7F != 0:
            right_attacks <<= 1
            
            attack_bitboard |= right_attacks
            right_attacks &= ~self.bb_occupy

        # Generate vertical (file) attacks  upward
        up_attacks = position & 0x00FFFFFFFFFFFFFF
        while up_attacks & 0x00FFFFFFFFFFFFFF != 0:
            up_attacks <<= 8
            
            attack_bitboard |= up_attacks
            up_attacks &= ~self.bb_occupy

        # Generate vertical (file) attacks downward
        down_attacks = position & 0xFFFFFFFFFFFFFF00
        while down_attacks & 0xFFFFFFFFFFFFFF00  != 0:
            down_attacks >>= 8
            
            attack_bitboard |= down_attacks
            down_attacks &= ~self.bb_occupy

        attack_bitboard &= rook_bitboard
        return attack_bitboard

    def bishop_moves(self, white, queen = False):
        # Initialize an empty bitboard for bishop attacks
        attack_bitboard = 0
        if queen:
            bishop_bitboard = self.bb_white_queens if white else self.bb_black_queens
        else:
            bishop_bitboard = self.bb_white_bishops if white else self.bb_black_bishops
        self_occupy = self.bb_white_occupy if white else self.bb_black_occupy
        # Generate attacks along the diagonals (up-right)
        up_left_attacks = bishop_bitboard & 0x00FEFEFEFEFEFEFE
        while up_left_attacks & 0x00FEFEFEFEFEFEFE != 0:
            up_left_attacks = (up_left_attacks << 7) 
            attack_bitboard |= up_left_attacks
            up_left_attacks &= ~self.bb_occupy & 0x00FEFEFEFEFEFEFE
            

        # Generate attacks along the diagonals (up-left)
        up_right_attacks = bishop_bitboard & 0x007F7F7F7F7F7F7F
        while up_right_attacks & 0x007F7F7F7F7F7F7F != 0:
            up_right_attacks = (up_right_attacks << 9)
            attack_bitboard |= up_right_attacks
            up_right_attacks &= ~self.bb_occupy & 0x007F7F7F7F7F7F7F

        # Generate attacks along the diagonals (down-left)
        down_left_attacks = bishop_bitboard & 0xFEFEFEFEFEFEFE00
        while down_left_attacks & 0xFEFEFEFEFEFEFE00 != 0:
            down_left_attacks = (down_left_attacks >> 9) 
            attack_bitboard |= down_left_attacks
            down_left_attacks &= ~self.bb_occupy & 0xFEFEFEFEFEFEFE00

        # Generate attacks along the diagonals (down-right)
        down_right_attacks = bishop_bitboard & 0x7F7F7F7F7F7F7F00
        while down_right_attacks & 0x7F7F7F7F7F7F7F00 != 0:
            down_right_attacks = (down_right_attacks >> 7) 
            attack_bitboard |= down_right_attacks
            down_right_attacks &= ~self.bb_occupy & 0x7F7F7F7F7F7F7F00

        return attack_bitboard & ~self_occupy

    def from_bishop_move(self, position, white, queen=False):
        # Initialize an empty bitboard for bishop attacks
        attack_bitboard = 0
        if queen:
            bishop_bitboard = self.bb_white_queens if white else self.bb_black_queens
        else:
            bishop_bitboard = self.bb_white_bishops if white else self.bb_black_bishops
        # Generate attacks along the diagonals (up-right)
        up_left_attacks = position & 0x00FEFEFEFEFEFEFE
        while up_left_attacks & 0x00FEFEFEFEFEFEFE != 0:
            up_left_attacks = (up_left_attacks << 7) 
            attack_bitboard |= up_left_attacks
            up_left_attacks &= ~self.bb_occupy & 0x00FEFEFEFEFEFEFE
            

        # Generate attacks along the diagonals (up-left)
        up_right_attacks = position & 0x007F7F7F7F7F7F7F
        while up_right_attacks & 0x007F7F7F7F7F7F7F != 0:
            up_right_attacks = (up_right_attacks << 9)
            attack_bitboard |= up_right_attacks
            up_right_attacks &= ~self.bb_occupy & 0x00FEFEFEFEFEFEFE

        # Generate attacks along the diagonals (down-left)
        down_left_attacks = position & 0xFEFEFEFEFEFEFE00
        while down_left_attacks & 0xFEFEFEFEFEFEFE00 != 0:
            down_left_attacks = (down_left_attacks >> 9) 
            attack_bitboard |= down_left_attacks
            down_left_attacks &= ~self.bb_occupy & 0xFEFEFEFEFEFEFE00

        # Generate attacks along the diagonals (down-right)
        down_right_attacks = position & 0x7F7F7F7F7F7F7F00
        while down_right_attacks & 0x7F7F7F7F7F7F7F00 != 0:
            down_right_attacks = (down_right_attacks >> 7) 
            attack_bitboard |= down_right_attacks
            down_right_attacks &= ~self.bb_occupy & 0x7F7F7F7F7F7F7F00

        attack_bitboard &= bishop_bitboard
        return attack_bitboard

    def queen_moves(self, white):
        return self.rook_moves(white,queen=True) | self.bishop_moves(white,queen=True)

    def from_queen_move(self, position, white):
        attack_bitboard = self.from_rook_move(position, white,queen=True) 
        attack_bitboard |= self.from_bishop_move(position,white,queen=True)
        return attack_bitboard

    def knight_moves(self, white):

        knight_bitboard = self.bb_white_knights if white else self.bb_black_knights
        self_occupy = self.bb_white_occupy if white else self.bb_black_occupy
        attack_bitboard = (knight_bitboard & 0xFCFCFCFCFCFCFC00) >> 10 #left 2 down A
        attack_bitboard |= (knight_bitboard & 0x003F3F3F3F3F3F3F) << 10 #right2 up  A
        attack_bitboard |= (knight_bitboard & 0x3F3F3F3F3F3F3F00) >> 6 #right 2 down A
        attack_bitboard |= (knight_bitboard & 0x00FCFCFCFCFCFCFC) << 6 #left2 up  A
        attack_bitboard |= (knight_bitboard & 0x7F7F7F7F7F7F0000) >> 15 #down 2 right  A
        attack_bitboard |= (knight_bitboard & 0x0000FEFEFEFEFEFE) << 15 #up2 left  A
        attack_bitboard |= (knight_bitboard & 0xFEFEFEFEFEFE0000) >> 17 #down 2 left
        attack_bitboard |= (knight_bitboard & 0x00007F7F7F7F7F7F) << 17 #up2 right
        return attack_bitboard & ~self_occupy

    def from_knight_move (self, position , white= True):
        knight_bitboard = self.bb_white_knights if white else self.bb_black_knights
        attack_bitboard = (position & 0xFCFCFCFCFCFCFC00) >> 10 #left 2 down A
        attack_bitboard |= (position & 0x003F3F3F3F3F3F3F) << 10 #right2 up  A
        attack_bitboard |= (position & 0x3F3F3F3F3F3F3F00) >> 6 #right 2 down A
        attack_bitboard |= (position & 0x00FCFCFCFCFCFCFC) << 6 #left2 up  A
        attack_bitboard |= (position & 0x7F7F7F7F7F7F0000) >> 15 #down 2 right  A
        attack_bitboard |= (position & 0x0000FEFEFEFEFEFE) << 15 #up2 left  A
        attack_bitboard |= (position & 0xFEFEFEFEFEFE0000) >> 17 #down 2 left
        attack_bitboard |= (position & 0x00007F7F7F7F7F7F) << 17 #up2 right
        attack_bitboard &= knight_bitboard
        return attack_bitboard

    def king_moves(self, white = True):
        king_bitboard = self.bb_white_king if white else self.bb_black_king
        self_occupy = self.bb_white_occupy if white else self.bb_black_occupy
        attack_bitboard = (king_bitboard & 0xFEFEFEFEFEFEFEFE) >> 1  # left
        attack_bitboard |= (king_bitboard & 0x7F7F7F7F7F7F7F7F) << 1  # right
        attack_bitboard |= (king_bitboard & 0x00FFFFFFFFFFFFFF) << 8  # Up
        attack_bitboard |= (king_bitboard & 0xFFFFFFFFFFFFFF00) >> 8  # Down
        attack_bitboard |= (king_bitboard & 0x7F7F7F7F7F7F7F00) >> 7  # Down Right
        attack_bitboard |= (king_bitboard & 0x00FEFEFEFEFEFEFE) << 7  # Up left
        attack_bitboard |= (king_bitboard & 0x007F7F7F7F7F7F7F) << 9  # Up Right
        attack_bitboard |= (king_bitboard & 0xFEFEFEFEFEFEFE00) >> 9  # Down Left
        
        if white:
            # Check if white king-side castling is possible
            if self.castling_rights & self.WHITE_KING_CASTLE and not (self.bb_occupy & 0x0000000000000060) and not self.is_positions_in_check(0x0000000000000070,white):
                attack_bitboard |= 0x0000000000000040  # King-side castling

            # Check if white queen-side castling is possible
            if self.castling_rights & self.WHITE_QUEEN_CASTLE and not (self.bb_occupy & 0x000000000000000E) and not self.is_positions_in_check(0x000000000000001C,white):
                attack_bitboard |= 0x0000000000000004  # Queen-side castling
        else:
            # Check if black king-side castling is possible
            if self.castling_rights & self.BLACK_KING_CASTLE and not (self.bb_occupy & 0x6000000000000000) and not self.is_positions_in_check(0x7000000000000000,white):
                attack_bitboard |= 0x4000000000000000  # King-side castling

            # Check if black queen-side castling is possible
            if self.castling_rights & self.BLACK_QUEEN_CASTLE and not (self.bb_occupy & 0x0E00000000000000) and not self.is_positions_in_check(0x1C00000000000000,white):
                attack_bitboard |= 0x0400000000000000  # Queen-side castling

        return attack_bitboard & ~self_occupy

    def is_positions_in_check(self, positions, white):
        if white:
            return (positions & (self.pawn_attacks(white = False) | self.knight_moves(white = False) | self.bishop_moves(white = False) | self.rook_moves(white = False) | self.queen_moves(white = False))) != 0 
        return (positions & (self.pawn_attacks(white = True) | self.knight_moves(white = True) | self.bishop_moves(white = True) | self.rook_moves(white = True) | self.queen_moves(white = True))) != 0

    def is_king_in_check(self, white=True):
        if white:
            return (self.bb_white_king & (self.pawn_attacks(white = False) | self.knight_moves(white = False) | self.bishop_moves(white = False) | self.rook_moves(white = False) | self.queen_moves(white = False))) != 0 
        return (self.bb_black_king & (self.pawn_attacks(white = True) | self.knight_moves(white = True) | self.bishop_moves(white = True) | self.rook_moves(white = True) | self.queen_moves(white = True))) != 0
    def play_input(self):
        while self.result == -1:
            self.display(self.whites_move)

            move = input("White to Move: " if self.whites_move else "Black to Move: ").strip()
            if move.lower() == "displaybb":
                self.display_bitboards()
            else:
                self.make_algebraic_move(move)
    def display(self, whites_perspective=True, players_perspective= False):
        print ("")
        if players_perspective:
            whites_perspective = self.whites_move
        if whites_perspective:
            for i, row in enumerate(self.board[::-1]):
                print(f"{8-i} {' '.join([Board.NUMBER_TO_PIECE.get(p,p) for p in row])}")
            print (f"  {' '.join(('A','B','C','D','E','F','G','H'))}")
        else:
            for i, row in enumerate (np.rot90(self.board, 2)[::-1]):
                print(f"{i+1} {' '.join([Board.NUMBER_TO_PIECE.get(p,p) for p in row])}")
            print (f"  {' '.join(('A','B','C','D','E','F','G','H')[::-1])}")

    def piece_at(self,coord, letter_rep = True , flipped = False):
        
        if flipped:
            b = np.rot90(self.board, 2)
        else:
            b = self.board
        if letter_rep:
            return Board.NUMBER_TO_PIECE.get(b[coord[1]][coord[0]])
        return b[coord[1]][coord[0]]
    

def test():
    b = Board("8/8/8/8/8/8/8/8 w KQkq - 0 1")
    for i in range(8):
        for j in range (8):
            b.board[i][j] = 5
            b.update_bitboards()
            b.display_bitboard(b.bb_white_queens)
            print()
            b.display_bitboard(b.queen_moves(True))
            print("-"*10)
            b.board[i][j] = 0

if __name__ == "__main__":

    board = Board("rq2k2r/p1p2ppp/8/1bppP3/5P2/8/PPP2nPP/RNQR2K1 w kq - 0 17")
    board.display()
    #board.play_input()

    print(board.get_to_from_square_algebraic_move("Kxf2",return_bitboard=False))




