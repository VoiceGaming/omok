import tkinter as tk
from tkinter import messagebox
from speech_recognizer_model import SpeechRecognizer,\
    LOADING, VOICE_INPUT, VOICE_CHECK, GAME_CHECK, GAME_OVER, ERROR, NO, YES

class Omok:
    def __init__(self, root, model):
        self.root = root
        self.root.title("Omok Game")

        self.board_size = 14
        self.cell_size = 40
        self.canvas_size = self.board_size * self.cell_size

        self.label = tk.Label(root, text="LOADING...", font=("Arial", 16, "bold"))
        self.label.pack()
        
        self.state_label = tk.Label(root, text=" ", font=("Arial", 12))
        self.state_label.pack()
        
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg="burlywood")
        self.canvas.pack()
        

        self.draw_board()
        self.board = [[None] * self.board_size for _ in range(self.board_size)]
        self.current_player = "black"

        self.model = model
        
        self.state = LOADING
        
        self.row = None
        self.col = None
        
        self.flg = True
        
        self.root.after(8000, self.state_machine)
        

    def draw_board(self):
        for i in range(self.board_size):
            for j in range(self.board_size):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")
                label = f"{chr(65+i)}{j+1}"
                self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=label, 
                                        font=("Arial", 10, "bold"), fill="gray")
                
    
    def check_winner(self, row, col):
        row = row - 1
        col = col - 1
        
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        player = self.board[row][col]
        
        for dr, dc in directions:
            count = 1
            for step in range(1, 5):
                r, c = row + dr * step, col + dc * step
                if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                    count += 1
                else:
                    break
            for step in range(1, 5):
                r, c = row - dr * step, col - dc * step
                if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                    count += 1
                else:
                    break
            if count >= 5:
                return True
        return False

    def place_stone_by_voice(self, row, col):
        row = row - 1
        col = col - 1
        if self.board[row][col] is None:
            x = col * self.cell_size + self.cell_size // 2
            y = row * self.cell_size + self.cell_size // 2
            color = "black" if self.current_player == "black" else "white"
            self.canvas.create_oval(x-15, y-15, x+15, y+15, fill=color, outline="black")
            
            self.board[row][col] = self.current_player
            
            # if self.check_winner(row, col):
            #     self.label.config(text=f"{self.current_player.capitalize()} Wins!")
            #     self.ask_restart()
            #     return GAME_OVER
            
            # self.current_player = "white" if self.current_player == "black" else "black"
            # self.label.config(text=f"{self.current_player.capitalize()}'s Turn")
            
            return True
        else:
            return False

    def reset_board(self):
        self.canvas.delete("all")
        self.draw_board()
        self.board = [[None] * self.board_size for _ in range(self.board_size)]
        self.current_player = "black"
        self.label.config(text="Black's Turn")


    def state_machine(self):
        if self.state == LOADING:
            self.label.config(text="Black's Turn")
            self.state_label.config(text=f"Voice Recognition...")
            self.state = VOICE_INPUT
        
        
        elif self.state == VOICE_INPUT:
            self.row, self.col = None, None
            while True:
                self.flg = False
                result = (self.model.listen())['text']
                self.row, self.col = self.model.parse_position_with_correction(result)

                if self.row is not None:  # 음성 입력이 올바르면 다음 상태로 이동
                    self.display_position(self.row, self.col)
                    self.flg = True
                    self.state = VOICE_CHECK
                    break

                self.state_label.config(text="Invalid Voice. Try again...")
        
        
        elif self.state == VOICE_CHECK:
            while True:
                self.flg = False
                result = (self.model.listen())['text']
                yes_or_no_or_error = self.model.yes_or_no(result)
                
                if yes_or_no_or_error != ERROR:
                    if yes_or_no_or_error == YES:
                        if self.place_stone_by_voice(self.row, self.col):
                            self.flg = True
                            self.state = GAME_CHECK
                        else:
                            self.state_label.config(text=f"Invalid Coordinate. Try again...")
                            self.flg = True
                            self.state = VOICE_INPUT
                    
                    elif yes_or_no_or_error == NO:
                        self.state_label.config(text=f"Voice Recognition...")
                        self.flg = True
                        self.state = VOICE_INPUT
                    
                    break
                
        
        elif self.state == GAME_CHECK:
            if self.check_winner(self.row, self.col):
                self.label.config(text=f"{self.current_player.capitalize()} Wins")
                self.state_label.config(text=f"Do you want to play again? (Yes/No)")
                self.flg = True
                self.state = GAME_OVER
                
            else:
                self.current_player = "white" if self.current_player == "black" else "black"
                self.label.config(text=f"{self.current_player.capitalize()}'s Turn")
                self.state_label.config(text=f"Voice Recognition...")
                self.flg = True
                self.state = VOICE_INPUT
            
        elif self.state == GAME_OVER:
            while True:
                self.flg = False
                result = (self.model.listen())['text']
                yes_or_no_or_error = self.model.yes_or_no(result)

                if yes_or_no_or_error != ERROR:
                    if yes_or_no_or_error == YES:
                        self.reset_board()
                        self.state_label.config(text=f"Voice Recognition...")
                        self.flg = True
                        self.state = LOADING
                        break
                    
                    elif yes_or_no_or_error == NO:
                        self.root.quit()
                        break
        
        self.root.after(10, self.state_machine)    
            
    def display_position(self, row, col):
        row_chr = chr(row + ord('A') - 1)
        col_chr = str(col)
        self.state_label.config(text=(row_chr+col_chr)+" is right? (Yes/No)")

            
if __name__ == "__main__":
    root = tk.Tk()
    model_path = r"vosk-model-small-en-us-0.15"
    grammar_path = r"grammar.json"
    model = SpeechRecognizer(model_path=model_path, grammar_file=grammar_path)
    game = Omok(root, model)
    root.mainloop()
