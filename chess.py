import tkinter as tk
from tkinter import messagebox
import threading
from chess_piece import Pawn, Rook, Knight, Bishop, Queen, King, WHITE, BLACK
from speech_recognizer_model import SpeechRecognizer, ERROR, NO, YES, CHESS

LOADING = 0
VOICE_INPUT_1 = 1
VOICE_INPUT_2 = 2
VOICE_CHECK = 3
GAME_CHECK = 4
GAME_OVER = 5

class ChessGame:
    def __init__(self, root, model):
        self.root = root
        self.root.title("Chess Game")
        
        self.board_size = 8
        self.cell_size = 60
        self.canvas_size = self.board_size * self.cell_size
        
        self.current_player = WHITE
        self.label = tk.Label(root, text="LOADING...", font=("Courier", 16, "bold"), width=35, anchor='center', justify='center')
        self.label.pack()
        
        self.state_label = tk.Label(root, text=" ", font=("Courier", 12), width=35, anchor='center', justify='center')
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
        
        self.voice_result = None
        
        self.root.after(8000, self.state_machine)
    
    def reset_board(self):
        """초기 체스 기물을 배치"""
        self.board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 체스 보드 생성
        self.current_player = WHITE
        self.game_set = False

        # 폰 (Pawn) 배치
        for col in range(8):
            self.board[6][col] = Pawn(WHITE)    # 백 폰
            self.board[1][col] = Pawn(BLACK)    # 흑 폰

        # 룩 (Rook)
        for col in (0, 7):
            self.board[7][col] = Rook(WHITE)    # 백 룩
            self.board[0][col] = Rook(BLACK)    # 흑 룩

        # 나이트 (Knight)
        for col in (1, 6):
            self.board[7][col] = Knight(WHITE)  # 백 나이트
            self.board[0][col] = Knight(BLACK)  # 흑 나이트

        # 비숍 (Bishop)
        for col in (2, 5):
            self.board[7][col] = Bishop(WHITE)  # 백 비숍
            self.board[0][col] = Bishop(BLACK)  # 흑 비숍

        # 퀸 (Queen)
        self.board[7][3] = Queen(WHITE) # 백 퀸
        self.board[0][3] = Queen(BLACK) # 흑 퀸
        
        # 킹 (King)
        self.board[7][4] = King(WHITE)  # 백 킹
        self.board[0][4] = King(BLACK)  # 흑 킹
    
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


    def is_path_clear(self, from_row, from_col, to_row, to_col):
        d_row = to_row - from_row
        d_col = to_col - from_col
        
        step_row = (d_row // abs(d_row)) if d_row != 0 else 0
        step_col = (d_col // abs(d_col)) if d_col != 0 else 0

        r, c = from_row + step_row, from_col + step_col

        while (r, c) != (to_row, to_col):
            if self.board[r][c] is not None:
                return False  # 경로에 기물이 있음
            r += step_row
            c += step_col

        return True  # 경로가 비어 있음


    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]

        if piece is None:
            return False
        if piece.color != self.current_player:
            return False
        if not piece.can_move(from_row, from_col, to_row, to_col):
            return False

        # 나이트가 아니면 경로 체크
        if not piece.is_knight and not self.is_path_clear(from_row, from_col, to_row, to_col):
            return False

        # 빈 칸 이동
        if target is None:
            if piece.is_pawn and (to_row==0 or to_row==7):
                self.board[to_row][to_col] = Queen(piece.color)
            else:
                self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = None
            piece.first = False
            return True

        # 적군 잡기
        if target.color != self.current_player:
            # 폰이면 대각선 공격인지 확인
            if piece.is_pawn:
                dy = to_row - from_row
                dx = abs(to_col - from_col)
                forward = -1 if piece.color == WHITE else 1
                if dy != forward or dx != 1:
                    return False

            # 킹 잡으면 게임 종료
            if target.is_king:
                self.game_set = True

            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = None
            piece.first = False
            return True

        return False  # 아군 기물이 있는 칸으로는 못 감
        
    
    def state_machine(self):
        if self.state == LOADING:
            self.label.config(text="White's Turn")
            self.state_label.config(text=f"Voice Recognition...")
            self.state = VOICE_INPUT_1
        
        
        elif self.state == VOICE_INPUT_1:
            self.from_row, self.from_col, self.to_row, self.to_col = None, None, None, None
            self.flg = False
            result = (self.model.listen())['text']
            self.from_row, self.from_col = self.model.parse_position_with_correction_chess(result)
            if self.from_row is not None:  # 음성 입력이 올바르면 다음 상태로 이동
                self.display_position_1()
                self.flg = True
                self.state = VOICE_INPUT_2
            else:
                self.state_label.config(text="Invalid Voice. Try again...")
                
        
        elif self.state == VOICE_INPUT_2:
            self.flg = False
            result = (self.model.listen())['text']
            if result == 'cancel':
                self.state_label.config(text=f"Voice Recognition...")
                self.flg = True
                self.state = VOICE_INPUT_1
            else:
                self.to_row, self.to_col = self.model.parse_position_with_correction_chess(result)
                if self.to_row is not None:  # 음성 입력이 올바르면 다음 상태로 이동
                    self.display_position_2()
                    self.flg = True
                    self.state = VOICE_CHECK
        
        
        elif self.state == VOICE_CHECK:
            self.flg = False
            result = (self.model.listen())['text']
            yes_or_no_or_error = self.model.yes_or_no(result)
                
            if yes_or_no_or_error != ERROR:
                if yes_or_no_or_error == YES:
                    if self.move_piece(self.from_row, self.from_col, self.to_row, self.to_col):
                        self.flg = True
                        self.state = GAME_CHECK
                    else:
                        self.state_label.config(text=f"Invalid Coordinate. Try again...")
                        self.flg = True
                        self.state = VOICE_INPUT_1
                
                elif yes_or_no_or_error == NO:
                    self.state_label.config(text=f"Voice Recognition...")
                    self.flg = True
                    self.state = VOICE_INPUT_1
                
        
        elif self.state == GAME_CHECK:
            self.update_board()
            if self.game_set:
                self.label.config(text=("White" if self.current_player==WHITE else "Black") + " Wins")
                self.state_label.config(text=f"Do you want to play again? (Yes/No)")
                self.flg = True
                self.state = GAME_OVER
                
            else:
                self.current_player = WHITE if self.current_player == BLACK else BLACK
                self.label.config(text=("White" if self.current_player==WHITE else "Black") + 's Turn')
                self.state_label.config(text=f"Voice Recognition...")
                self.flg = True
                self.state = VOICE_INPUT_1
            
        elif self.state == GAME_OVER:
            self.flg = False
            result = (self.model.listen())['text']
            yes_or_no_or_error = self.model.yes_or_no(result)

            if yes_or_no_or_error != ERROR:
                if yes_or_no_or_error == YES:
                    self.reset_board()
                    self.update_board()
                    self.state_label.config(text=f"Voice Recognition...")
                    self.flg = True
                    self.state = LOADING
                
                elif yes_or_no_or_error == NO:
                    self.root.quit()
        
        self.root.after(5, self.state_machine)    
            
    def display_position_1(self):
        from_col_chr = chr(self.from_col + ord('A'))
        from_row_chr = str(8-self.from_row)
        
        self.state_label.config(text=(from_col_chr+from_row_chr)+" to where? (or Cancel)")
    
    def display_position_2(self):
        from_col_chr = chr(self.from_col + ord('A'))
        to_col_chr = chr(self.to_col + ord('A'))
        
        from_row_chr = str(8-self.from_row)
        to_row_chr = str(8-self.to_row)
        
        self.state_label.config(text=(from_col_chr+from_row_chr)+" to "+ (to_col_chr+to_row_chr) + " is right? (Yes/No)")
        

if __name__ == "__main__":
    root = tk.Tk()
    model_path = r"vosk-model-small-en-us-0.15"
    grammar_path = r"grammar_chess.json"
    model = SpeechRecognizer(model_path=model_path, grammar_file=grammar_path, game=CHESS)
    game = ChessGame(root, model)
    root.mainloop()
