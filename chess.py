import tkinter as tk
from tkinter import messagebox
from chess_piece import Pawn, Rook, Knight, Bishop, Queen, King, WHITE, BLACK
from speech_recognizer_model import SpeechRecognizer,\
    LOADING, VOICE_INPUT, VOICE_CHECK, GAME_CHECK, GAME_OVER, ERROR, NO, YES, CHESS
    
FIRST = 2
    
class ChessGame:
    def __init__(self, root, model):
        self.root = root
        self.root.title("Chess Game")
        
        self.board_size = 8
        self.cell_size = 60
        self.canvas_size = self.board_size * self.cell_size
        
        self.current_player = WHITE
        self.label = tk.Label(root, text="LOADING...", font=("Arial", 16, "bold"))
        self.label.pack()
        
        self.state_label = tk.Label(root, text=" ", font=("Arial", 12))
        self.state_label.pack()
        
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()
        
        self.board = None
        self.draw_board()
        self.reset_board()
        self.update_board()
        
        self.model = model
        
        self.game_set = False
        
        self.state = LOADING
        
        self.from_row = None
        self.from_col = None
        self.to_row = None
        self.to_col = None
        
        self.flg = True
        
        self.root.after(8000, self.state_machine)
    
    def reset_board(self):
        """초기 체스 기물을 배치"""
        self.board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 체스 보드 생성
        self.current_player = WHITE
        self.game_set = False

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

                # 체스 좌표(A1, B2 등) 계산
                coord_text = f"{chr(65 + col)}{8 - row}"  # 예: A1, B2 ...
                
                # 각 칸의 오른쪽 위 모서리에 좌표 표시 (작은 글씨로)
                self.canvas.create_text(x2 - 5, y1 + 5, text=coord_text, font=("Arial", 10, 'bold'), anchor="ne", fill="#B58763" if (row + col) % 2 == 0 else "#F0DAB5", tags="coordinate")
                self.canvas.tag_raise("coordinate")
        
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
                                                text=piece_unicode, font=("Arial", 25), tags="pieces")
                    else:
                        self.canvas.create_text((x1 + x1 + self.cell_size) / 2, (y1 + y1 + self.cell_size) / 2,
                                                text=piece_unicode, font=("Arial", 25, 'bold'), tags="pieces")

        # 턴 표시 업데이트
        # if self.current_player == WHITE:
        #     self.label.config(text="White's Turn")
        # else:
        #     self.label.config(text="Black's Turn")
            
    def move_piece(self, from_row, from_col, to_row, to_col):
        if self.board[from_row][from_col] is None:
            return False
        elif self.board[from_row][from_col].color != self.current_player:
            return False
        elif self.board[from_row][from_col].can_move(to_row, to_col):
            if self.board[to_row][to_col] is None:
                self.board[to_row][to_col] = self.board[from_row][from_col]
                self.board[from_row][from_col] = None
                self.board[to_row][to_col].row, self.board[to_row][to_col].row = to_row, to_col
                self.board[to_row][to_col].first = False
                return True
            elif self.board[to_row][to_col].color != self.current_player:
                if self.board[to_row][to_col].is_king:
                    self.game_set = True
                elif self.board[to_row][to_col].is_pawn:
                    dy = to_row - from_row
                    if dy != (-1 if self.color == WHITE else 1) or abs(to_col-from_col) != 1:
                        return False
                self.board[to_row][to_col] = self.board[from_row][from_col]
                self.board[from_row][from_col] = None
                self.board[to_row][to_col].row, self.board[to_row][to_col].row = to_row, to_col
                self.board[to_row][to_col].first = False
                return True
            else:
                return False
        else:
            return False
        
    
    def state_machine(self):
        if self.state == LOADING:
            self.label.config(text=" ")
            self.label.config(text="White's Turn")
            self.state_label.config(text=f" ")
            self.state_label.config(text=f"Voice Recognition...")
            self.state = VOICE_INPUT
        
        
        elif self.state == VOICE_INPUT:
            self.from_row, self.from_col, self.to_row, self.to_col = None, None, None, None
            self.flg = False
            result = (self.model.listen())['text']
            self.from_row, self.from_col, self.to_row, self.to_col = self.model.parse_position_with_correction_chess(result)
            if self.from_row is not None:  # 음성 입력이 올바르면 다음 상태로 이동
                self.display_position()
                self.flg = True
                self.state = VOICE_CHECK
            else:
                self.state_label.config(text=" ")
                self.state_label.config(text="Invalid Voice. Try again...")
        
        
        elif self.state == VOICE_CHECK:
            self.flg = False
            result = (self.model.listen_yes_or_no())['text']
            yes_or_no_or_error = self.model.yes_or_no(result)
                
            if yes_or_no_or_error != ERROR:
                if yes_or_no_or_error == YES:
                    if self.move_piece(self.from_row, self.from_col, self.to_row, self.to_col):
                        self.flg = True
                        self.state = GAME_CHECK
                    else:
                        self.state_label.config(text=f" ")
                        self.state_label.config(text=f"Invalid Coordinate. Try again...")
                        self.flg = True
                        self.state = VOICE_INPUT
                
                elif yes_or_no_or_error == NO:
                    self.state_label.config(text=f" ")
                    self.state_label.config(text=f"Voice Recognition...")
                    self.flg = True
                    self.state = VOICE_INPUT
                
        
        elif self.state == GAME_CHECK:
            self.update_board()
            if self.game_set:
                self.label.config(text=f" ")
                self.label.config(text="White" if self.current_player==WHITE else "Black" + " Wins")
                self.state_label.config(text=f" ")
                self.state_label.config(text=f"Do you want to play again? (Yes/No)")
                self.flg = True
                self.state = GAME_OVER
                
            else:
                self.current_player = WHITE if self.current_player == BLACK else BLACK
                self.label.config(text=f" ")
                self.label.config(text="White" if self.current_player==WHITE else "Black" + 's Turn')
                self.state_label.config(text=f"")
                self.state_label.config(text=f"Voice Recognition...")
                self.flg = True
                self.state = VOICE_INPUT
            
        elif self.state == GAME_OVER:
            self.flg = False
            result = (self.model.listen_yes_or_no())['text']
            yes_or_no_or_error = self.model.yes_or_no(result)

            if yes_or_no_or_error != ERROR:
                if yes_or_no_or_error == YES:
                    self.reset_board()
                    self.update_board()
                    self.state_label.config(text=f" ")
                    self.state_label.config(text=f"Voice Recognition...")
                    self.flg = True
                    self.state = LOADING
                
                elif yes_or_no_or_error == NO:
                    self.root.quit()
        
        self.root.after(5, self.state_machine)    
            
    def display_position(self):
        from_col_chr = chr(self.from_col + ord('A'))
        to_col_chr = chr(self.to_col + ord('A'))
        
        from_row_chr = str(8-self.from_row)
        to_row_chr = str(8-self.to_row)
        
        self.state_label.config(text=" ")
        self.state_label.config(text=(from_col_chr+from_row_chr)+" to "+ (to_col_chr+to_row_chr) + " is right? (Yes/No)")
        

if __name__ == "__main__":
    root = tk.Tk()
    model_path = r"vosk-model-small-en-us-0.15"
    grammar_path = r"grammar_chess.json"
    model = SpeechRecognizer(model_path=model_path, grammar_file=grammar_path, game=CHESS)
    game = ChessGame(root, model)
    root.mainloop()
