import tkinter as tk
from io import BytesIO
from PIL import Image, ImageOps, ImageTk


IMAGE_DISPLAY_SIZE = (520, 390)
RESAMPLE_FILTER = getattr(Image, "Resampling", Image).LANCZOS

class QuizUI:
    def __init__(self, root, quiz_manager):
        self.root = root
        self.quiz = quiz_manager
        self.time_limit = 45
        self.time_left = self.time_limit
        self.timer_id = None
        self.correct_answer = ""
        self.choice_buttons = []
        self.menu_widgets = []
        self.review_session_rows = []
        self.paused = False

        self.setup_ui()
        self.show_entry_screen()

    def setup_ui(self):
        self.root.title("Geography Quiz")

        self.image_label = tk.Label(self.root)

        self.question_label = tk.Label(self.root, font=("Arial", 16))

        self.choices_frame = tk.Frame(self.root)

        self.answer_entry = tk.Entry(self.root, font=("Arial", 14))
        self.submit_button = tk.Button(self.root, text="Submit", font=("Arial", 12),
                                       command=self.check_answer)
        self.skip_button = tk.Button(self.root, text="Skip", font=("Arial", 12),
                                     command=self.skip_question)
        self.pause_button = tk.Button(self.root, text="Pause", font=("Arial", 12),
                                      command=self.toggle_pause)
        self.stop_button = tk.Button(self.root, text="Stop Quiz", font=("Arial", 12),
                                     command=self.stop_quiz)

        self.feedback_label = tk.Label(self.root, font=("Arial", 12))

        self.score_label = tk.Label(self.root, font=("Arial", 12))

        self.timer_label = tk.Label(self.root, font=("Arial", 12), fg="blue")

        self.toggle_button = tk.Button(self.root, text="Toggle Visual/Text Mode", font=("Arial", 12),
                                       command=self.toggle_mode)
        self.toggle_button = tk.Button(self.root, text="Switch to Text Mode", font=("Arial", 12),
                                       command=self.toggle_mode)

    def clear_menu_widgets(self):
        for widget in self.menu_widgets:
            widget.destroy()
        self.menu_widgets.clear()

    def hide_quiz_widgets(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        for btn in self.choice_buttons:
            btn.destroy()
        self.choice_buttons.clear()

        for widget in (
            self.image_label,
            self.question_label,
            self.choices_frame,
            self.answer_entry,
            self.submit_button,
            self.skip_button,
            self.pause_button,
            self.stop_button,
            self.feedback_label,
            self.score_label,
            self.timer_label,
        ):
            widget.pack_forget()

    def show_entry_screen(self):
        self.hide_quiz_widgets()
        self.clear_menu_widgets()

        title = tk.Label(self.root, text="Geography Quiz", font=("Arial", 22, "bold"))
        start_button = tk.Button(self.root, text="Start Quiz", font=("Arial", 14), command=self.start_full_quiz)
        review_button = tk.Button(self.root, text="Review Quiz Results", font=("Arial", 14), command=self.show_results_screen)

        for widget in (title, start_button, review_button):
            widget.pack(pady=10)
            self.menu_widgets.append(widget)

    def show_quiz_widgets(self):
        self.image_label.pack(pady=10)
        self.question_label.pack(pady=10)
        self.choices_frame.pack()
        self.feedback_label.pack()
        self.score_label.pack()
        self.timer_label.pack()

    def start_full_quiz(self):
        self.clear_menu_widgets()
        self.quiz.start_session()
        self.show_quiz_widgets()
        self.next_question()

    def start_retry_quiz(self, session_id):
        questions = self.quiz.retry_questions(session_id)
        self.clear_menu_widgets()
        if not questions:
            message = tk.Label(self.root, text="No missed, skipped, or timed-out questions to retry.", font=("Arial", 14))
            back_button = tk.Button(self.root, text="Back to Results", font=("Arial", 12), command=self.show_results_screen)
            for widget in (message, back_button):
                widget.pack(pady=10)
                self.menu_widgets.append(widget)
            return

        self.quiz.start_session(questions)
        self.show_quiz_widgets()
        self.next_question()

    def show_results_screen(self):
        self.hide_quiz_widgets()
        self.clear_menu_widgets()

        title = tk.Label(self.root, text="Quiz Results", font=("Arial", 18, "bold"))
        title.pack(pady=8)
        self.menu_widgets.append(title)

        self.review_session_rows = self.quiz.latest_sessions()
        if not self.review_session_rows:
            message = tk.Label(self.root, text="No quiz results yet.", font=("Arial", 14))
            back_button = tk.Button(self.root, text="Back", font=("Arial", 12), command=self.show_entry_screen)
            for widget in (message, back_button):
                widget.pack(pady=8)
                self.menu_widgets.append(widget)
            return

        listbox = tk.Listbox(self.root, width=78, height=10, font=("Consolas", 10))
        for row in self.review_session_rows:
            session_id, started_at, completed_at, score, total_questions, skipped = row
            completed_text = "complete" if completed_at else "in progress"
            listbox.insert(
                tk.END,
                f"#{session_id:<4} {started_at:%Y-%m-%d %H:%M:%S}  "
                f"{self.format_score(float(score))}/{total_questions}  skipped:{skipped}  {completed_text}",
            )
        listbox.select_set(0)
        listbox.pack(pady=8)
        self.menu_widgets.append(listbox)

        review_button = tk.Button(
            self.root,
            text="Review Missed & Skipped",
            font=("Arial", 12),
            command=lambda: self.show_missed_skipped_review(self.selected_session_id(listbox)),
        )
        retry_button = tk.Button(
            self.root,
            text="Redo Missed/Skipped Only",
            font=("Arial", 12),
            command=lambda: self.start_retry_quiz(self.selected_session_id(listbox)),
        )
        start_button = tk.Button(self.root, text="Start New Quiz", font=("Arial", 12), command=self.start_full_quiz)
        back_button = tk.Button(self.root, text="Back", font=("Arial", 12), command=self.show_entry_screen)
        for widget in (review_button, retry_button, start_button, back_button):
            widget.pack(pady=4)
            self.menu_widgets.append(widget)

    def selected_session_id(self, listbox):
        selection = listbox.curselection()
        index = selection[0] if selection else 0
        return self.review_session_rows[index][0]

    def show_missed_skipped_review(self, session_id):
        self.hide_quiz_widgets()
        self.clear_menu_widgets()

        title = tk.Label(self.root, text=f"Missed & Skipped Review - Session #{session_id}", font=("Arial", 16, "bold"))
        title.pack(pady=8)
        self.menu_widgets.append(title)

        attempts = self.quiz.review_attempts(session_id)
        review_text = tk.Text(self.root, width=95, height=22, font=("Consolas", 10), wrap=tk.WORD)
        if not attempts:
            review_text.insert(tk.END, "No missed, skipped, or timed-out questions in this quiz.")
        else:
            for _, question_index, category, prompt, correct_answer, user_answer, status, points in attempts:
                review_text.insert(
                    tk.END,
                    f"{question_index}. [{status.upper()}] {category or 'quiz'}\n"
                    f"   Q: {prompt}\n"
                    f"   Your answer: {user_answer or '-'}\n"
                    f"   Correct: {correct_answer}\n"
                    f"   Points: {points}\n\n",
                )
        review_text.config(state=tk.DISABLED)
        review_text.pack(pady=8)
        self.menu_widgets.append(review_text)

        retry_button = tk.Button(
            self.root,
            text="Redo Missed/Skipped Only",
            font=("Arial", 12),
            command=lambda: self.start_retry_quiz(session_id),
        )
        back_button = tk.Button(self.root, text="Back to Results", font=("Arial", 12), command=self.show_results_screen)
        home_button = tk.Button(self.root, text="Home", font=("Arial", 12), command=self.show_entry_screen)
        for widget in (retry_button, back_button, home_button):
            widget.pack(pady=4)
            self.menu_widgets.append(widget)

    def toggle_mode(self):
        current = self.quiz.is_visual_mode()
        self.quiz.set_visual_mode(not current)
        new_label = "Switch to Visual Mode" if current else "Switch to Text Mode"
        self.toggle_button.config(text=new_label)
        self.feedback_label.config(text=f"{'Visual' if not current else 'Text'} Mode Activated", fg="blue")

    def show_image(self, image_source, is_binary=False):
        try:
            if is_binary:
                img = Image.open(BytesIO(bytes(image_source)))
            else:
                print(f"Trying to load image: {image_source}")
                img = Image.open(image_source)
            img = ImageOps.contain(img, IMAGE_DISPLAY_SIZE, RESAMPLE_FILTER)
            self.tk_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.tk_image, text="")
        except Exception:
            self.image_label.config(text="Image not found", image="")

    def start_timer(self):
        self.time_left = self.time_limit
        self.update_timer()

    def update_timer(self):
        if self.paused:
            return

        self.timer_label.config(text=f"Time left: {self.time_left}s")
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.quiz.record_attempt(self.quiz.current_question, "", "timeout", 0)
            self.feedback_label.config(text=f"⏰ Time's up! Correct answer: {self.correct_answer}", fg="orange")
            self.update_score_display()
            self.root.after(1500, self.next_question)

    def next_question(self):
        self.paused = False
        self.pause_button.config(text="Pause")
        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        for btn in self.choice_buttons:
            btn.destroy()
        self.choice_buttons.clear()
        self.answer_entry.pack_forget()
        self.submit_button.pack_forget()
        self.skip_button.pack_forget()

        question = self.quiz.get_next_question()
        if not question:
            self.end_quiz()
            return

        self.correct_answer = question["correct_answer"]
        prompt_key = "visual_prompt" if self.quiz.is_visual_mode() else "text_prompt"
        self.question_label.config(text=question[prompt_key])

        self.show_image(question["image_source"], question["is_binary_image"])
        self.feedback_label.config(text="")

        if self.quiz.get_mode() == "multiple_choice":
            choices = self.quiz.get_choices(self.correct_answer, question["answer_kind"])
            for choice in choices:
                btn = tk.Button(self.choices_frame, text=choice, font=("Arial", 12),
                                command=lambda c=choice: self.check_answer(c))
                btn.pack(pady=5)
                self.choice_buttons.append(btn)
        else:
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.pack()
            self.submit_button.pack()

        self.skip_button.pack(pady=8)
        self.pause_button.pack(pady=4)
        self.stop_button.pack(pady=4)
        self.start_timer()

    def check_answer(self, selected_choice=None):
        if self.paused:
            return

        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        user_answer = selected_choice if selected_choice else self.answer_entry.get()
        correct = self.quiz.check_answer(user_answer, self.correct_answer)

        if correct:
            self.quiz.score += 1
            self.quiz.record_attempt(self.quiz.current_question, user_answer, "correct", 1)
            self.feedback_label.config(text="✅ Correct!", fg="green")
        else:
            self.quiz.record_attempt(self.quiz.current_question, user_answer, "incorrect", 0)
            self.feedback_label.config(text=f"❌ Incorrect. The correct answer is {self.correct_answer}.", fg="red")

        self.update_score_display()
        self.root.after(1500, self.next_question)

    def skip_question(self):
        if self.paused:
            return

        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        self.quiz.skipped += 1
        self.quiz.score += 0.5
        self.quiz.record_attempt(self.quiz.current_question, "", "skipped", 0.5)
        self.feedback_label.config(text=f"⏭️ Skipped. Correct answer: {self.correct_answer}", fg="orange")
        self.update_score_display()
        self.root.after(1000, self.next_question)

    def toggle_pause(self):
        if self.paused:
            self.paused = False
            self.pause_button.config(text="Pause")
            self.feedback_label.config(text="")
            self.set_answer_controls_state(tk.NORMAL)
            self.update_timer()
            return

        self.paused = True
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.pause_button.config(text="Resume")
        self.feedback_label.config(text="⏸️ Paused", fg="blue")
        self.set_answer_controls_state(tk.DISABLED)

    def set_answer_controls_state(self, state):
        self.answer_entry.config(state=state)
        self.submit_button.config(state=state)
        self.skip_button.config(state=state)
        for button in self.choice_buttons:
            button.config(state=state)

    def stop_quiz(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        self.quiz.finish_session()
        self.show_entry_screen()

    def update_score_display(self):
        total_answered = self.quiz.current_index
        percentage = round((self.quiz.score / total_answered) * 100, 1) if total_answered else 0
        self.score_label.config(
            text=f"Score: {self.format_score(self.quiz.score)} / {total_answered} ({percentage}%) | Skipped: {self.quiz.skipped}"
        )

    def end_quiz(self):
        self.quiz.finish_session()
        total_answered = self.quiz.current_index
        self.question_label.config(text="🎉 Quiz Complete!")
        self.feedback_label.config(
            text=f"Final Score: {self.format_score(self.quiz.score)} / {total_answered} | Skipped: {self.quiz.skipped}"
        )
        self.timer_label.config(text="")
        for btn in self.choice_buttons:
            btn.config(state=tk.DISABLED)
        self.answer_entry.pack_forget()
        self.submit_button.pack_forget()
        self.skip_button.pack_forget()
        self.pause_button.pack_forget()
        self.stop_button.pack_forget()

        session_id = self.quiz.session_id
        review_button = tk.Button(
            self.root,
            text="Review Missed & Skipped",
            font=("Arial", 12),
            command=lambda: self.show_missed_skipped_review(session_id),
        )
        retry_button = tk.Button(
            self.root,
            text="Redo Missed/Skipped Only",
            font=("Arial", 12),
            command=lambda: self.start_retry_quiz(session_id),
        )
        home_button = tk.Button(self.root, text="Home", font=("Arial", 12), command=self.show_entry_screen)
        for widget in (review_button, retry_button, home_button):
            widget.pack(pady=4)
            self.menu_widgets.append(widget)

    @staticmethod
    def format_score(score):
        return str(int(score)) if score.is_integer() else str(score)