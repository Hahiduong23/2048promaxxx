import tkinter as tk
import random
from tkinter import messagebox
from abc import ABC, abstractmethod

class GameMode(ABC):
    def __init__(self,root):
        self._root = root
        self._board = Board()
    @abstractmethod
    def key_pressed(self, event):
        pass
    def start_game(self):
        pass
    def show_game_over(self, message):
        replay = messagebox.askeysno('2048', f'{message}\n Chơi lại 0?')
        if replay:
            self._board.reset()
            self.update_grid_ui()
        else:
            self._root.quit()
# Lớp Tile đại diện cho từng ô trên bảng
class Tile:
    def __init__(self, value=0):
        self.__value = value 

    def set_value(self, value):
        self.__value = value

    def get_value(self):
        return self.__value

# Lớp Board xử lý các thao tác trên bảng 2048
class Board:
    def __init__(self):
        self.__grid = [[Tile() for _ in range(4)] for _ in range(4)]
        self.__best_score = 0  
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self.__grid[i][j].get_value() == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.__grid[i][j].set_value(2)

    def get_grid_values(self):
        return [[self.__grid[i][j].get_value() for j in range(4)] for i in range(4)]

    def compress(self):
        changed = False
        new_grid = [[Tile() for _ in range(4)] for _ in range(4)]
        for i in range(4):
            pos = 0
            for j in range(4):
                if self.__grid[i][j].get_value() != 0:
                    new_grid[i][pos].set_value(self.__grid[i][j].get_value())
                    if j != pos:
                        changed = True
                    pos += 1
        self.__grid = new_grid
        return changed

    def merge(self):
        changed = False
        for i in range(4):
            for j in range(3):
                if self.__grid[i][j].get_value() == self.__grid[i][j + 1].get_value() and self.__grid[i][j].get_value() != 0:
                    new_value = self.__grid[i][j].get_value() * 2
                    self.__grid[i][j].set_value(new_value)
                    self.__grid[i][j + 1].set_value(0)
                    changed = True
                    if new_value > self.__best_score:
                        self.__best_score = new_value
        return changed

    def reverse(self):
        for i in range(4):
            self.__grid[i] = self.__grid[i][::-1]

    def transpose(self):
        self.__grid = [list(row) for row in zip(*self.__grid)]

    def move_left(self):
        changed1 = self.compress()
        changed2 = self.merge()
        self.compress()
        return changed1 or changed2

    def move_right(self):
        self.reverse()
        changed = self.move_left()
        self.reverse()
        return changed

    def move_up(self):
        self.transpose()
        changed = self.move_left()
        self.transpose()
        return changed

    def move_down(self):
        self.transpose()
        changed = self.move_right()
        self.transpose()
        return changed

    def check_state(self):
        for i in range(4):
            for j in range(4):
                if self.__grid[i][j].get_value() == 2048:
                    return 'WON'
        for i in range(4):
            for j in range(4):
                if self.__grid[i][j].get_value() == 0:
                    return 'GAME NOT OVER'
        for i in range(3):
            for j in range(3):
                if self.__grid[i][j].get_value() == self.__grid[i + 1][j].get_value() or self.__grid[i][j].get_value() == self.__grid[i][j + 1].get_value():
                    return 'GAME NOT OVER'
        for j in range(3):
            if self.__grid[3][j].get_value() == self.__grid[3][j + 1].get_value():
                return 'GAME NOT OVER'
        for i in range(3):
            if self.__grid[i][3].get_value() == self.__grid[i + 1][3].get_value():
                return 'GAME NOT OVER'
        return 'LOST'

    # Getter for best score
    def get_best_score(self):
        return self.__best_score

    # Reset the board for replay
    def reset(self):
        self.__grid = [[Tile() for _ in range(4)] for _ in range(4)]
        self.add_new_tile()
        self.add_new_tile()

# Lớp Game2048 quản lý giao diện và luồng trò chơi
class Game2048(GameMode):
    def __init__(self, root):
        super().__init__(root)
        self._root = root 
        self._root.title("2048")
        self._root.geometry("400x450")
        self._board = Board()
        self.create_widgets()
        self.update_grid_ui()
    

    def create_widgets(self):
        self._frame = tk.Frame(self._root, bg="#bbada0")
        self._frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self._tiles = [[tk.Label(self._frame, text="", width=4, height=2, bg="#cdc1b4", font=('Arial', 24, 'bold'), anchor='center') for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                self._tiles[i][j].grid(row=i, column=j, padx=5, pady=5, sticky='nsew')
        for i in range(4):
            self._frame.grid_columnconfigure(i, weight=1)
            self._frame.grid_rowconfigure(i, weight=1)

        self._score_label = tk.Label(self._root, text="Best Score: 0", font=('Arial', 18))
        self._score_label.pack()
        
        self._root.bind("<Key>", self.key_pressed)

    def update_grid_ui(self):
        grid_values = self._board.get_grid_values()
        for i in range(4):
            for j in range(4):
                value = grid_values[i][j]
                color = self.get_color(value)
                text = str(value) if value != 0 else ''
                self._tiles[i][j].config(text=text, bg=color)

        # Cập nhật best score
        best_score = self._board.get_best_score()
        self._score_label.config(text=f"Best Score: {best_score}")

    def get_color(self, value):
        colors = {
            2: '#fdd0dc', 4: '#fcb3c2', 8: '#f8a2b7',
            16: '#f7819f', 32: '#f76c7c', 64: '#f64d65',
            128: '#f64d6f', 256: '#f65f6f', 512: '#f67272',
            1024: '#f67d7d', 2048: '#f68888'
        }
        return colors.get(value, '#faf8ef')

    def key_pressed(self, event):
        if event.keysym == 'Up':
            changed = self._board.move_up()
        elif event.keysym == 'Down':
            changed = self._board.move_down()
        elif event.keysym == 'Left':
            changed = self._board.move_left()
        elif event.keysym == 'Right':
            changed = self._board.move_right()
        else:
            return
        if changed:
            self._board.add_new_tile()
        self.update_grid_ui()
        state = self._board.check_state()
        if state == 'WON':
            self.show_game_over("Chúc mừng! Bạn đã thắng!")
        elif state == 'LOST':
            self.show_game_over("Game Over! Bạn đã thua!")
    


    def show_game_over(self, message):
        replay = messagebox.askyesno("2048", f"{message}\nBạn có muốn chơi lại không?")
        if replay:
            self._board.reset()
            self.update_grid_ui()
        else:
            self._root.destroy()  # Đóng cửa sổ trò chơi hiện tại
            root = tk.Tk()  # Tạo lại cửa sổ root
            menu = ModeSelection(root)  # Gọi lại menu chọn chế độ chơi
            root.mainloop()


# Lớp Game2048EasyMode kế thừa từ Game2048, ghi đè phương thức start_game và reset
class Game2048EasyMode(Game2048):
    def __init__(self, root):
        super().__init__(root)
        self.start_game() 

    def create_widgets(self):
        super().create_widgets()

    def update_grid_ui(self):
        super().update_grid_ui()

    # Phương thức khởi động trò chơi, chỉ tạo 1 ô có giá trị là 8
    def start_game(self):
        # Reset bảng nhưng không thêm bất kỳ ô mới nào sau khi reset
        self._board._Board__grid = [[Tile() for _ in range(4)] for _ in range(4)]
        # Đặt một ô đầu tiên với giá trị là 8
        empty_cells = [(i, j) for i in range(4) for j in range(4)]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self._board._Board__grid[i][j].set_value(8)  
        self.update_grid_ui()  
    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self._board.get_grid_values()[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self._board._Board__grid[i][j].set_value(8)

    # Ghi đè phương thức reset để đảm bảo chỉ tạo ô 8 sau khi chơi lại
    def reset(self):
        self._board._Board__grid = [[Tile() for _ in range(4)] for _ in range(4)]
        empty_cells = [(i, j) for i in range(4) for j in range(4)]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self._board._Board__grid[i][j].set_value(8)  
        self.update_grid_ui() 


class Game2048CompetitionMode(Game2048):
    def __init__(self, root):
        super().__init__(root)
        self.move_counter = 0  # Bắt đầu số lần di chuyển từ 0
        self.update_move_counter()  

    def create_widgets(self):
        super().create_widgets()
        self._move_label = tk.Label(self._root, text="Moves: 0", font=('Arial', 18))
        self._move_label.pack()

    def update_move_counter(self):
        self._move_label.config(text=f"Moves: {self.move_counter}")

    def key_pressed(self, event):
        changed = False
        if event.keysym == 'Up':
            changed = self._board.move_up()
        elif event.keysym == 'Down':
            changed = self._board.move_down()
        elif event.keysym == 'Left':
            changed = self._board.move_left()
        elif event.keysym == 'Right':
            changed = self._board.move_right()
        else:
            return

        if changed:
            self._board.add_new_tile()  # Thêm ô mới với giá trị 2
            self.move_counter += 1  # Tăng số lần di chuyển
            self.update_move_counter()  
        self.update_grid_ui() 

        # Kiểm tra trạng thái trò chơi
        state = self._board.check_state()
        if state == 'WON':
            self.show_game_over(f"Chúc mừng! Bạn đã thắng với {self.move_counter} nước đi!")
        elif state == 'LOST':
            self.show_game_over(f"Game Over! Bạn đã thua sau {self.move_counter} nước đi!")

    def show_game_over(self, message):
        # Gọi phương thức show_game_over từ lớp cha
        super().show_game_over(message)

        self.move_counter = 0  # Đặt lại số lần di chuyển về 0
        self.update_move_counter()  # Cập nhật lại giao diện hiển thị số lần di chuyển
            

class ModeSelection:
    def __init__(self, root):
        self._root = root
        self._root.title("2048 - Chọn chế độ chơi")
        self._root.geometry("300x250")  
        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self._root, text="Chọn chế độ chơi:", font=('Arial', 16))
        label.pack(pady=20)

        normal_button = tk.Button(self._root, text="Normal Mode", font=('Arial', 14), command=self.start_normal_mode)
        normal_button.pack(pady=10)

        easy_button = tk.Button(self._root, text="Easy Mode", font=('Arial', 14), command=self.start_easy_mode)
        easy_button.pack(pady=10)

        competition_button = tk.Button(self._root, text="Competition Mode", font=('Arial', 14), command=self.start_competition_mode)
        competition_button.pack(pady=10)

    def start_normal_mode(self):
        self._root.destroy()  # Đóng cửa sổ menu
        root = tk.Tk()
        game = Game2048(root)
        root.mainloop()

    def start_easy_mode(self):
        self._root.destroy()  # Đóng cửa sổ menu
        root = tk.Tk()
        game = Game2048EasyMode(root)
        root.mainloop()

    def start_competition_mode(self):
        self._root.destroy()  # Đóng cửa sổ menu
        root = tk.Tk()
        game = Game2048CompetitionMode(root)  # Sử dụng chế độ mới
        root.mainloop()

# Khởi động menu chọn chế độ chơi
if __name__ == "__main__":
    root = tk.Tk()
    menu = ModeSelection(root)
    root.mainloop()
