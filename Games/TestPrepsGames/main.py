from Games.TestPrepsGames.quiz_manager import QuizManager
from Games.TestPrepsGames.quiz_ui import QuizUI
from Games.TestPrepsGames.db_config import get_db_config
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    quiz_manager = QuizManager(get_db_config())
    quiz_manager.set_mode("text")
    quiz_ui = QuizUI(root, quiz_manager)
    root.mainloop()