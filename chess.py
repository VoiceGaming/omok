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
        
        self.label = tk.Label(root, text="White's Turn", font=("Arial", 16, "bold"))
        self.label.pack()
        
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()
        
        self.board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 체스 보드 생성
        self.white_pieces = []
        self.black_pieces = []
        self.setup_pieces()
        self.draw_board()
        
        self.current_player = WHITE
    
    def setup_pieces(self):
        """초기 체스 기물을 배치"""
        # 폰 (Pawn) 배치
        for col in range(8):
            self.white_pieces.append(Pawn(1, col, WHITE))  # 백 폰
            self.black_pieces.append(Pawn(6, col, BLACK))  # 흑 폰

        # 룩 (Rook)
        for col in (0, 7):
            self.white_pieces.append(Rook(0, col, WHITE))  # 백 룩
            self.black_pieces.append(Rook(7, col, BLACK))  # 흑 룩

        # 나이트 (Knight)
        for col in (1, 6):
            self.white_pieces.append(Rook(0, col, WHITE))  # 백 나이트
            self.black_pieces.append(Rook(7, col, BLACK))  # 흑 나이트

        # 비숍 (Bishop)
        for col in (2, 5):
            self.white_pieces.append(Rook(0, col, WHITE))  # 백 비숍
            self.black_pieces.append(Rook(7, col, BLACK))  # 흑 비숍

        # 퀸 (Queen)
        self.white_pieces.append(Queen(0, 3, WHITE))    # 백 퀸
        self.black_pieces.append(Queen(7, 3, BLACK))    # 흑 퀸
        
        # 킹 (King)
        self.white_pieces.append(King(0, 4, WHITE))    # 백 킹
        self.black_pieces.append(King(7, 4, BLACK))    # 흑 킹
        
    def draw_board(self):
        colors = ["#EEEED2", "#769656"]
        for i in range(self.board_size):
            for j in range(self.board_size):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                color = colors[(i + j) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    # def place_pieces(self):
    #     self.pieces = {}
    #     piece_order = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        
    #     for i in range(self.board_size):
    #         self.pieces[(1, i)] = self.create_piece("P", "black", 1, i)
    #         self.pieces[(6, i)] = self.create_piece("P", "white", 6, i)
    #         self.pieces[(0, i)] = self.create_piece(piece_order[i], "black", 0, i)
    #         self.pieces[(7, i)] = self.create_piece(piece_order[i], "white", 7, i)

    def create_piece(self, piece, color, row, col):
        x, y = col * self.cell_size + self.cell_size // 2, row * self.cell_size + self.cell_size // 2
        piece_id = self.canvas.create_text(x, y, text=piece, font=("Arial", 24, "bold"), fill=color)
        return (piece, color, piece_id)
    
    def on_click(self, event):
        col, row = event.x // self.cell_size, event.y // self.cell_size
        
        if self.selected_piece:
            self.move_piece(self.selected_piece, row, col)
            self.selected_piece = None
        elif (row, col) in self.pieces and self.pieces[(row, col)][1] == self.current_player:
            self.selected_piece = (row, col)
    
    def move_piece(self, from_pos, to_row, to_col):
        from_row, from_col = from_pos
        
        if (to_row, to_col) in self.pieces and self.pieces[(to_row, to_col)][1] == self.current_player:
            return
        
        piece, color, piece_id = self.pieces.pop(from_pos)
        x, y = to_col * self.cell_size + self.cell_size // 2, to_row * self.cell_size + self.cell_size // 2
        self.canvas.coords(piece_id, x, y)
        self.pieces[(to_row, to_col)] = (piece, color, piece_id)
        
        self.current_player = "black" if self.current_player == "white" else "white"
        self.label.config(text=f"{self.current_player.capitalize()}'s Turn")

if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
