WHITE = True
BLACK = False

class ChessPiece:
    def __init__(self, color):
        self.color = color
        self.is_king = False
        self.is_pawn = False
        self.is_knight = False
        self.first = True
        
    def can_move(self, from_row, from_col, target_row, target_col):
        raise NotImplementedError
    
    def get_unicode(self):
        raise NotImplementedError
        
class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.is_pawn = True
    
    def can_move(self, from_row, from_col, target_row, target_col):
        dy = target_row - from_row
        dx = target_col - from_col
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
    def __init__(self, color):
        super().__init__(color)
    
    def can_move(self, from_row, from_col, target_row, target_col):
        return from_row == target_row or from_col == target_col  # 같은 행 또는 열
    
    def get_unicode(self):
        # 폰 유니코드 반환
        if self.color == WHITE:
            return "♖"
        else:
            return "♜"
        
class Knight(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.is_knight = True
    
    def can_move(self, from_row, from_col, target_row, target_col):
        dy = abs(target_row - from_row)
        dx = abs(target_col - from_col)
        return (dx, dy) in [(1, 2), (2, 1)]  # L자 형태 이동
    
    def get_unicode(self):
        # 폰 유니코드 반환
        if self.color == WHITE:
            return "♘"
        else:
            return "♞"
        
class Bishop(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
    
    def can_move(self, from_row, from_col, target_row, target_col):
        return abs(target_row - from_row) == abs(target_col - from_col)  # 대각선 이동
    
    def get_unicode(self):
        if self.color == WHITE:
            return "♗"
        else:
            return "♝"
        
class Queen(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
    
    def can_move(self, from_row, from_col, target_row, target_col):
        return (abs(target_row - from_row) == abs(target_col - from_col)) or \
               (from_row == target_row or from_col == target_col)  # 대각선 + 직선 이동
    
    def get_unicode(self):
        if self.color == WHITE:
            return "♕"
        else:
            return "♛"
    
    
        
class King(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.is_king = True
    
    def can_move(self, from_row, from_col, target_row, target_col):
        return max(abs(target_row - from_row), abs(target_col - from_col)) == 1  # 한 칸 이동
    
    def get_unicode(self):
        if self.color == WHITE:
            return "♔"
        else:
            return "♚"