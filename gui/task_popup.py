import math
import queue
import threading
import tkinter as tk
from tkinter import ttk

WIDTH = 500
HEIGHT = 300
BIG_RADIUS = 30

# Colors for the loading symbol
COLORS = ["#282a2b", "#404142", "#5d5f61", "#6e7073", "#85888c", "#9b9fa3", "#b1b7bd", "#b1b7bd", "#b1b7bd", "#f0f7ff"]

CHECK_RESULT_RATE = 500  # ms
LOADING_ANIMATION_RATE = 80  # ms


class TaskPopup:
    def __init__(self, master=None, func=None, args=(), caption=None):
        """
        Create the TaskPopup widget.

        :param master: the master window of the widget (the parent)
        :param func: the blocking function to execute
        :param args: the args of the blocking function, as a tuple
        :param caption: caption to show at the user
        """
        self._func = func
        self._args = args

        self._top_level = tk.Toplevel(master)
        self._top_level.title("WAIT")

        # Positioning the top level window
        window_width = self._top_level.winfo_reqwidth()
        window_height = self._top_level.winfo_reqheight()

        position_x = int(self._top_level.winfo_screenwidth() / 2 - window_width)
        position_y = int(self._top_level.winfo_screenheight() / 2 - window_height / 1.5)

        self._top_level.geometry(str(WIDTH) + "x" + str(HEIGHT) + "+" + str(position_x) + "+" + str(position_y))
        self._top_level.resizable(False, False)
        # Setting the grab -> all events are direct to this widget, so the master window can't be used
        # (it is not interactive, cause all events come here)
        # That line of code make the window modal
        self._top_level.grab_set()

        self._main_frame = ttk.Frame(self._top_level, style="Light.TFrame")
        self._main_frame.pack(expand=1, fill=tk.BOTH)

        # Drawing the loading sign
        self._main_canvas = tk.Canvas(master=self._main_frame, width=WIDTH, height=HEIGHT, bg="#161922", bd=0,
                                      highlightthickness=0)
        self._main_canvas.pack(expand=1, fill=tk.BOTH)

        w = int(self._main_canvas['width']) / 2
        h = int(self._main_canvas['height']) / 2

        radius = 2  # radius of little circles
        n_of_points = 10
        angle = 0
        offset_angle = 360 / n_of_points

        index = 0
        self._circles = []
        for _ in range(n_of_points):
            x = BIG_RADIUS * math.cos(math.radians(angle)) + w
            y = BIG_RADIUS * math.sin(math.radians(angle)) + h

            self._circles.append(
                self._main_canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=COLORS[index],
                                              outline=COLORS[index]))

            angle += offset_angle
            index += 1

        if caption is not None:
            self._main_canvas.create_text(w, h + h / 2, text=caption, fill="#ffffff")

        # Communication with thread
        self._queue = queue.Queue()
        self._result = None

        # Worker thread
        self._thread = threading.Thread(
            daemon=False,
            target=self._func_to_run,
            args=(self._args, self._queue)
        )

        self._after_result = None
        self._after_loading = None

    @property
    def top_level(self):
        return self._top_level

    @property
    def result(self):
        return self._result

    def check_for_result(self):
        if self._thread.is_alive():
            self._after_result = self._top_level.after(CHECK_RESULT_RATE, self.check_for_result)
        else:

            try:
                self._result = self._queue.get(block=False)
            except queue.Empty:
                self._after_result = self._top_level.after(CHECK_RESULT_RATE, self.check_for_result)
                return

            self._top_level.after_cancel(self._after_result)
            self._after_result = None

            self._top_level.grab_release()  # it is not necessary -> destroy implies grab releasing
            self._top_level.destroy()

    def _update_loading(self):
        if self._thread.is_alive():
            first_color = COLORS.pop(0)
            COLORS.append(first_color)
            index = 0
            for circle_id in self._circles:
                self._main_canvas.itemconfigure(circle_id, fill=COLORS[index], outline=COLORS[index])
                index += 1
            self._after_loading = self._top_level.after(LOADING_ANIMATION_RATE, self._update_loading)
        else:
            self._top_level.after_cancel(self._after_loading)
            self._after_loading = None

    def start(self):
        self._thread.start()
        self._after_result = self._top_level.after(CHECK_RESULT_RATE, self.check_for_result)
        self._after_loading = self._top_level.after(LOADING_ANIMATION_RATE, self._update_loading)

    def _func_to_run(self, args, _queue):
        result = self._func(*args)
        _queue.put(result)
