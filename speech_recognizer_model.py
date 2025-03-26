import vosk
import sounddevice as sd
import queue
import json
import sys

LOADING = 0
VOICE_INPUT = 1
VOICE_CHECK = 2
GAME_CHECK = 3
GAME_OVER = 4

ERROR = 0
NO = 1
YES = 2

class SpeechRecognizer:
    def __init__(self, model_path, grammar_file, samplerate=16000):
        self.model_path = model_path
        self.grammar_file = grammar_file
        self.samplerate = samplerate
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, self.samplerate)
        
        with open(self.grammar_file, "r", encoding="utf-8") as f:
            grammar_data = json.load(f)
            self.words_list = grammar_data["words"]
        
        self.recognizer.SetGrammar(json.dumps(self.words_list))
        self.audio_queue = queue.Queue()
        self.stream = None

    def callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.audio_queue.put(bytes(indata))

    def listen(self):
        self.stream = sd.RawInputStream(samplerate=self.samplerate, blocksize=1500, dtype='int16',
                                        channels=1, callback=self.callback)
        self.stream.start()
        
        while True:
            data = self.audio_queue.get()
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                self.stop()  # 음성 인식 완료 후 종료
                return result

    def stop(self):
        if self.stream:
            self.stream.stop()  # 음성 스트림 종료
            
    def yes_or_no(self, words):
        words = words.lower().split()
        if len(words) != 1:
            return ERROR
        
        word = words[0]
        
        if word == "yes":
            return YES
        elif word == "no":
            return NO
        else:
            return ERROR
        
    def word_to_number(self, word):
        # 숫자 단어를 숫자로 매핑
        word_map = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14
        }

        return word_map[word]

    def parse_position_with_correction(self, position):
        words = position.lower().split()
        if len(words) != 2:
            return None, None

        row_char = words[0]
        col_str = words[1]

        if row_char == "eight":
            row_char = "a"
        if col_str == "a":
            col_str = "eight"

        col = self.word_to_number(col_str)
        
        if not row_char.isalpha() or not col:
            return None, None

        row = ord(row_char.upper()) - ord('A') + 1

        return row, col