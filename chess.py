import tkinter as tk
from tkinter import messagebox
from chess_piece import Pawn, Rook, Knight, Bishop, Queen, King, WHITE, BLACK

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        
        self.board_size = 8
        self.cell_size = 60
        self.canvas_size = self.board_size * self.cell_size
        
        self.current_player = WHITE
        self.label = tk.Label(root, text="White's Turn", font=("Arial", 16, "bold"))
        self.label.pack()
        
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()
        
        self.board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 체스 보드 생성
        self.draw_board()
        self.setup_pieces()
        self.update_board()
        
    
    def setup_pieces(self):
        """초기 체스 기물을 배치"""
        # 폰 (Pawn) 배치
        for col in range(8):
            self.board[6][col] = Pawn(6, col, WHITE)    # 백 폰
            self.board[1][col] = Pawn(1, col, BLACK)    # 흑 폰

        # 룩 (Rook)
        for col in (0, 7):
            self.board[7][col] = Rook(7, col, WHITE)    # 백 룩
            self.board[0][col] = Rook(0, col, BLACK)    # 흑 룩

        # 나이트 (Knight)
        for col in (1, 6):
            self.board[7][col] = Knight(7, col, WHITE)  # 백 나이트
            self.board[0][col] = Knight(0, col, BLACK)  # 흑 나이트

        # 비숍 (Bishop)
        for col in (2, 5):
            self.board[7][col] = Bishop(7, col, WHITE)  # 백 비숍
            self.board[0][col] = Bishop(0, col, BLACK)  # 흑 비숍

        # 퀸 (Queen)
        self.board[7][3] = Queen(7, 3, WHITE) # 백 퀸
        self.board[0][3] = Queen(0, 3, BLACK) # 흑 퀸
        
        # 킹 (King)
        self.board[7][4] = King(7, 4, WHITE)  # 백 킹
        self.board[0][4] = King(0, 4, BLACK)  # 흑 킹
    
    def draw_board(self):
        """체스판 그리기"""
        # 체스판의 각 칸을 그리기
        for row in range(self.board_size):
            for col in range(self.board_size):
                # 칸의 좌표 계산
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # 흰색과 검은색 칸을 번갈아 그리기
                color = "#F0DAB5" if (row + col) % 2 == 0 else "#B58763"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
        
        # 좌표 (A-H, 1-8) 그리기
        for row in range(self.board_size):
            # 왼쪽에 행 번호 (1~8) 그리기
            self.canvas.create_text(20, (row * self.cell_size) + self.cell_size / 2, 
                                    text=str(8 - row), font=("Arial", 12, "bold"))
        
        for col in range(self.board_size):
            # 아래에 열 알파벳 (A-H) 그리기
            self.canvas.create_text((col * self.cell_size) + self.cell_size / 2, self.canvas_size - 20, 
                                    text=chr(65 + col), font=("Arial", 12, "bold"))


        
    def update_board(self):
        """체스판을 UI에 업데이트"""
        self.canvas.delete("pieces")  # 이전에 그려진 모든 요소를 삭제

        # 각 기물을 체스판에 유니코드로 그리기
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece:
                    # 유니코드 기물 출력
                    piece_unicode = piece.get_unicode()  # 각 기물의 유니코드 반환하는 메소드 필요
                    x1 = col * self.cell_size
                    y1 = row * self.cell_size
                    if piece.color == WHITE:
                        self.canvas.create_text((x1 + x1 + self.cell_size) / 2, (y1 + y1 + self.cell_size) / 2,
                                                text=piece_unicode, font=("Arial", 40), tags="pieces")
                    else:
                        self.canvas.create_text((x1 + x1 + self.cell_size) / 2, (y1 + y1 + self.cell_size) / 2,
                                                text=piece_unicode, font=("Arial", 40, 'bold'), tags="pieces")

        # 턴 표시 업데이트
        if self.current_player == WHITE:
            self.label.config(text="White's Turn")
        else:
            self.label.config(text="Black's Turn")
            
    def move_piece(self, from_row, from_col, to_row, to_col):
        if ~self.board[from_row][from_col]:
            return False
        elif self.board[from_row][from_col].color != self.current_player:
            return False
        elif ~self.board[to_row][to_col] or self.board[to_row][to_col].color != self.current_player:
            if self.board[from_row][from_col].can_move(to_row, to_col):
                self.board[to_row][to_col] = self.board[from_row][from_col]
                self.board[from_row][from_col] = None
                return True
            else:
                return False
        else:
            return False

if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
