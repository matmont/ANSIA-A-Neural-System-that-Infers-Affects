import tkinter as tk
from tkinter import ttk
from tkinter import IntVar, StringVar, DoubleVar

import random

WIDTH = 700
HEIGHT = 600

DURATION = 1000  # seconds

COLORS = {
    'BLUE': '#4848EF',
    'RED': '#FF0000',
    'YELLOW': '#FFEC2C',
    'GREEN': '#29B229',
    'PURPLE': '#B200FF',
    'ORANGE': '#FFA600',
    'PINK': '#FF65F6',
    'BROWN': '#99320B',
    'WHITE': '#FFFFFF',
}


class StroopTest:
    def __init__(self, master=None):
        self._top_level = tk.Toplevel(master)
        self._top_level.title("Stroop Test")

        # Positioning the top level window
        window_width = self._top_level.winfo_reqwidth()
        window_height = self._top_level.winfo_reqheight()

        position_x = int(self._top_level.winfo_screenwidth() / 2 - window_width)
        position_y = int(self._top_level.winfo_screenheight() / 2 - window_height / 1.5)

        self._top_level.geometry(str(WIDTH) + "x" + str(HEIGHT) + "+" + str(position_x) + "+" + str(position_y))
        self._top_level.resizable(False, False)

        self._time_remaining = IntVar(value=DURATION)
        self._time_after_job = self._top_level.after(1000, self._decrease_time_remaining)

        # Current word (the text)
        self._current_word = StringVar(value='N/A')
        # Current color (the color of the text)
        self._current_color = StringVar(value='N/A')
        self._current_accuracy = DoubleVar(value=0.0)
        self._total_questions = 0
        self._right_questions = 0

        # Creating the layout

        main_frame = ttk.Frame(self._top_level, style="Red.TFrame")
        main_frame.pack(expand=1, fill=tk.BOTH)

        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=4)
        main_frame.rowconfigure(2, weight=3)
        main_frame.columnconfigure(0, weight=1)

        stats_frame = ttk.Frame(main_frame, style='Yellow.TFrame')
        stats_frame.grid(row=0, column=0, sticky='nwes')
        stats_frame.rowconfigure(0, weight=1)
        stats_frame.columnconfigure(0, weight=1)

        labels_frame = ttk.Frame(stats_frame, style='Light.TFrame')
        labels_frame.grid(row=0, column=0, sticky='nwes')
        # Remaining time
        remaining_time_label = ttk.Label(labels_frame, text='Remaining time: ')
        remaining_time_label.pack(side=tk.LEFT, padx=10)
        remaining_time = ttk.Label(labels_frame, textvariable=self._time_remaining)
        remaining_time.pack(side=tk.LEFT, padx=(0, 20))

        # Current accuracy
        accuracy_label = ttk.Label(labels_frame, text='Accuracy: ')
        accuracy_label.pack(side=tk.LEFT, padx=10)
        accuracy = ttk.Label(labels_frame, textvariable=self._current_accuracy)
        accuracy.pack(side=tk.LEFT, padx=(0, 5))
        perc = ttk.Label(labels_frame, text='%')
        perc.pack(side=tk.LEFT)

        word_frame = ttk.Frame(main_frame, style='Red.TFrame')
        word_frame.grid(row=1, column=0, sticky='nwes')
        word_frame.rowconfigure(0, weight=1)
        word_frame.columnconfigure(0, weight=1)

        self._current_word_label = ttk.Label(word_frame, textvariable=self._current_word, style="Big.TLabel")
        self._current_word_label.grid(row=0, column=0, sticky='nwes')

        buttons_frame = ttk.Frame(main_frame, style='Green.TFrame')
        buttons_frame.grid(row=2, column=0, sticky='nwes')

        # Creating buttons for answers
        self._buttons = []
        for i in range(0, 2):
            buttons_frame.rowconfigure(i, weight=1)
            for j in range(0, 3):
                buttons_frame.columnconfigure(j, weight=1)
                btn = ttk.Button(buttons_frame, text='N/A')
                btn.bind('<Button-1>', self._button_click)
                btn.grid(row=i, column=j, sticky='nwes')
                self._buttons.append(btn)

        self._new_question()

    @property
    def top_level(self):
        return self._top_level

    def _decrease_time_remaining(self):
        """
        This function decrease the remaining time.
        """
        self._time_remaining.set(self._time_remaining.get() - 1)
        self._time_after_job = self._top_level.after(1000, self._decrease_time_remaining)
        if self._time_remaining.get() <= 0:
            # If the time is over we want to restart the counter (for simplicity)
            self._time_remaining.set(DURATION)
            self._current_accuracy.set(0.0)
            self._total_questions = 0
            self._right_questions = 0
            self._new_question()

    def clear_after_jobs(self):
        self._top_level.after_cancel(self._time_after_job)

    def _new_question(self):
        """
        This function take a random question from the group of questions selected. Also, it shows it.
        """
        # Retrieving data for the current word. Let's choose a color to write the text and a color to color it
        random_tuple_1 = random.choice(list(COLORS.items()))
        random_tuple_2 = random.choice(list(COLORS.items()))
        while random_tuple_1[0] == random_tuple_2[0]:
            random_tuple_1 = random.choice(list(COLORS.items()))
            random_tuple_2 = random.choice(list(COLORS.items()))
        color_name_1 = random_tuple_1[0]
        color_name_2 = random_tuple_2[0]  # This is the color name to guess
        color_value_2 = random_tuple_2[1]
        self._current_word.set(color_name_1)
        self._current_word_label['foreground'] = color_value_2

        self._current_color.set(color_name_2)  # color to guess

        pick_from_list = list(COLORS.keys())
        # 'color_name_2' and 'color_name_1' are already selected so we get rid out of them
        # from 'pick_from_list' (from which we will select randomly 4 element)
        pick_from_list.remove(color_name_2)
        pick_from_list.remove(color_name_1)
        buttons_labels = [color_name_1, color_name_2] + random.sample(pick_from_list, 4)
        random.shuffle(buttons_labels)
        for i in range(len(self._buttons)):
            self._buttons[i]['text'] = buttons_labels[i]

    def _button_click(self, event):
        """
        This method handle the click on an answer button
        :param event: the click Event
        """
        choice = event.widget['text']
        if choice == self._current_color.get():
            self._right_questions += 1
        else:
            self._time_remaining.set(self._time_remaining.get() - 10)  # penalty!
        self._total_questions += 1
        self._current_accuracy.set(float('% .2f' % (self._right_questions / self._total_questions * 100)))
        self._new_question()
