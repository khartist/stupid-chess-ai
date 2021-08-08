import operator
from itertools import product


class ChessPiece:

    eatenPieces = []
    moveHistory = []
    positionHistory = []
    x = 0
    y = 0

    def __init__(self, color, x, y):
        self.moved = False
        self.color = color
        self.x = x
        self.y = y
        self.type = self.__class__.__name__

    def filter_moves(self, moves, board):
        final_moves = moves[:]
        for move in moves:
            board.make_move(self, move[0], move[1], keep_history=True)
            if board.king_is_threatened(self.color):
                final_moves.remove(move)
            board.unmake_move(self)
        return final_moves

    def get_moves(self, prevent_king_death=False):
        pass

    def get_last_eaten(self):
        return self.eatenPieces.pop()

    def set_last_eaten(self, piece):
        self.eatenPieces.append(piece)

    def set_position(self, x, y, keep_history):
        if keep_history:
            self.positionHistory.append(self.x)
            self.positionHistory.append(self.y)
            self.moveHistory.append(self.moved)
        self.x = x
        self.y = y
        self.moved = True

    def set_old_position(self):
        position_y = self.positionHistory.pop()
        position_x = self.positionHistory.pop()
        self.y = position_y
        self.x = position_x

    def set_moved_previous(self):
        self.moved = self.moveHistory.pop()

    def __repr__(self):
        return '{}: {}'.format(self.type, self.color)


class Bishop(ChessPiece):

    def get_moves(self, board, prevent_king_death=False):
        moves = []
        add = operator.add
        sub = operator.sub
        operators = [(add, add), (add, sub), (sub, add), (sub, sub)]
        for ops in operators:
            for i in range(1, 9):
                x = ops[0](self.x, i)
                y = ops[1](self.y, i)
                if not board.is_valid_move(x, y) or board.has_friend(self, x, y) and not prevent_king_death:
                    break
                if board.has_empty_block(x, y):
                    moves.append((x, y))
                if board.has_opponent(self, x, y) or board.has_friend(self, x, y) and prevent_king_death:
                    moves.append((x, y))
                    break
        return moves


class Rook(ChessPiece):

    def get_moves(self, board, prevent_king_death=False):
        moves = []
        moves += self.get_vertical_moves(board, prevent_king_death)
        moves += self.get_horizontal_moves(board, prevent_king_death)
        return moves

    def get_vertical_moves(self, board, prevent_king_death):
        moves = []
        for op in [operator.add, operator.sub]:
            for i in range(1, 9):
                x = op(self.x, i)
                if not board.is_valid_move(x, self.y) or board.has_friend(self, x, self.y) and not prevent_king_death:
                    break
                if board.has_empty_block(x, self.y):
                    moves.append((x, self.y))
                if board.has_opponent(x, self.y) or board.has_friend(self, x, self.y) and prevent_king_death:
                    moves.append((x, self.y))
                    break
        return moves

    def get_horizontal_moves(self, board, prevent_king_death):
        moves = []
        for op in [operator.add, operator.sub]:
            for i in range(1, 9):
                y = op(self.y, i)
                if not board.is_valid_move(self.x, y) or board.has_friend(self, self.x, y) and not prevent_king_death:
                    break
                if board.has_empty_block(self.x, y):
                    moves.append((self.x, y))
                if board.has_opponent(self.x, y) or board.has_friend(self, self.x, y) and prevent_king_death:
                    moves.append((self.x, y))
                    break
        return moves


class Queen(ChessPiece):

    def get_moves(self, board):
        moves = []
        rook = Rook(self.color)
        rook.set_position(self.x, self.y, False)
        bishop = Bishop(self.color)
        bishop.set_position(self.x, self.y, False)
        moves.append(rook.get_moves(board))
        moves.append(bishop.get_moves(board))
        return moves


class King(ChessPiece):

    def get_moves(self, board, prevent_king_death=False):
        moves = []
        moves += self.get_horizontal_moves(board, prevent_king_death)
        moves += self.get_vertical_moves(board, prevent_king_death)
        return moves

    def get_vertical_moves(self, board, prevent_king_death):
        moves = []
        for op in [operator.add, operator.sub]:
            x = op(self.x, 1)
            if board.has_empty_block(x, self.y) or board.has_opponent(self, x, self.y) or board.has_friend(self, x, self.y) and prevent_king_death:
                moves.append((x, self.y))
            if board.has_empty_block(x, self.y + 1) or board.has_opponent(self, x, self.y + 1) or board.has_friend(self, x, self.y + 1) and prevent_king_death:
                moves.append((x, self.y+1))
            if board.has_empty_block(x, self.y - 1) or board.has_opponent(self, x, self.y - 1) or board.has_friend(self, x, self.y - 1) and prevent_king_death:
                moves.append((x, self.y - 1))
        return moves

    def get_horizontal_moves(self, board, prevent_king_death):
        moves = []
        for op in [operator.add, operator.sub]:
            y = op(self.y, 1)
            if board.has_empty_block(self.x, y) or board.has_opponent(self, self.x, y) or board.has_friend(self, self.x, y) and prevent_king_death:
                moves.append((self.x, y))
        return moves


class Pawn(ChessPiece):

    def get_moves(self, board, prevent_king_death=False):
        moves = []
        if board.game_mode == 0 and self.color == 'white' or board.game_mode == 1 and self.color == 'black':
            direction = 1
        else:
            direction = -1
        x = self.x + direction
        if board.has_empty_block(x, self.y) and not prevent_king_death:
            moves.append((x, self.y))
            if self.moved is False and board.has_empty_block(x + direction, self.y):
                moves.append((x + direction, self.y))
        if board.is_valid_move(x, self.y - 1):
            if board.has_opponent(self, x, self.y - 1) or ((board.has_empty_block(x, self.y - 1) or board.has_firend(self, x, self.y - 1)) and prevent_king_death):
                moves.append((x, self.y - 1))
        if board.is_valid_move(self.x + direction, self.y + 1):
            if board.has_opponent(self, x, self.y + 1) or ((board.has_empty_block(x, self.y + 1) or board.has_firend(self, x, self.y + 1)) and prevent_king_death):
                moves.append((x, self.y + 1))
        return moves


class Knight(ChessPiece):

    def get_moves(self, board, prevent_king_death=False):
        moves = []
        add = operator.add
        sub = operator.sub
        op_list = [(add, sub), (sub, add), (add, add), (sub, sub)]
        nums = [(1, 2), (2, 1)]
        combinations = list(product(op_list, nums))
        for comb in combinations:
            x = comb[0][0](self.x, comb[1][0])
            y = comb[0][1](self.y, comb[1][1])
            if board.has_empty_block(x, y) or board.has_opponent(self, x, y) or board.has_friend(self, x, y) and prevent_king_death:
                moves.append((x, y))
        return moves
