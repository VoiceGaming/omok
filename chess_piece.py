WHITE = True
BLACK = False

class ChessPiece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.is_king = False
        self.is_pawn = False
        self.first = True
        
    def can_move(self, target_row, target_col):
        raise NotImplementedError
    
    def get_unicode(self):
        raise NotImplementedError
        
class Pawn(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.pawn = True
    
    def can_move(self, target_row, target_col):
        dy = target_row - self.row
        dx = target_col - self.col
        if self.first and dy == 2 * (-1 if self.color == WHITE else 1) and dx == 0:
            return True  # 처음에만 두 칸 이동 가능
        if dy == (-1 if self.color == WHITE else 1):
            if dx == 0 or abs(dx) == 1:
                return True # 체스판에서 판단
        return False
    
    def get_unicode(self):
        # 폰 유니코드 반환
        if self.color == WHITE:
            return "♙"
        else:
            return "♟"
        
class Rook(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
    
    def can_move(self, target_row, target_col):
        return self.row == target_row or self.col == target_col  # 같은 행 또는 열
    
    def get_unicode(self):
        # 폰 유니코드 반환
        if self.color == WHITE:
            return "♖"
        else:
            return "♜"
        
class Knight(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
    
    def can_move(self, target_row, target_col):
        dy = abs(target_row - self.row)
        dx = abs(target_col - self.col)
        return (dx, dy) in [(1, 2), (2, 1)]  # L자 형태 이동
    
    def get_unicode(self):
        # 폰 유니코드 반환
        if self.color == WHITE:
            return "♘"
        else:
            return "♞"
        
class Bishop(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
    
    def can_move(self, target_row, target_col):
        return abs(target_row - self.row) == abs(target_col - self.col)  # 대각선 이동
    
    def get_unicode(self):
        if self.color == WHITE:
            return "♗"
        else:
            return "♝"
        
class Queen(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
    
    def can_move(self, target_row, target_col):
        return (abs(target_row - self.row) == abs(target_col - self.col)) or \
               (self.row == target_row or self.col == target_col)  # 대각선 + 직선 이동
    
    def get_unicode(self):
        if self.color == WHITE:
            return "♕"
        else:
            return "♛"
    
    
        
class King(ChessPiece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.is_king = True
    
    def can_move(self, target_row, target_col):
        return max(abs(target_row - self.row), abs(target_col - self.col)) == 1  # 한 칸 이동
    
    def get_unicode(self):
        if self.color == WHITE:
            return "♔"
        else:
            return "♚"