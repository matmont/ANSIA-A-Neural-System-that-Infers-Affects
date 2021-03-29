import queue
import threading
import tkinter as tk
from tkinter import IntVar, DoubleVar
from tkinter import ttk
from tkinter.messagebox import askokcancel

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gui import util as util_gui
from gui.wesad_mode import master_thread_implementation
from gui.wesad_mode import stroop_test, quiz_test
from shimmer import util

SELECTED_THEME = util_gui.DRIBBBLE_THEME

WINDOW_SIZE = 40


class PredictionPage:
    """
    PredictionPage shows the predictions of the classifier to the user. It uses a real time plot from matplotlib.
    """
    def __init__(self, master=None, shimmers=None, model=None):
        self._master = master
        self._shimmers = shimmers
        self._model = model

        self._top_level = tk.Toplevel(master=self._master)
        self._top_level.title("Prediction")
        self._top_level.geometry("1280x720")
        self._top_level.protocol("WM_DELETE_WINDOW", self._handle_close)

        # UI - top part of the window

        # This variable tell if the current state should be stress or not, so it is possible
        # to compute the accuracy of the predictor
        self._stress = IntVar(value=0)
        self._threshold = DoubleVar(value=0.5)
        self._threshold_view = False
        self._accuracy = DoubleVar(value=0.0)
        self._prec_accuracy = -1

        self._frame = ttk.Frame(self._top_level, style="Light.TFrame")
        self._frame.pack(expand=1, fill=tk.BOTH)
        # Stress frame
        self._stress_frame = ttk.Frame(self._frame, style="Light.TFrame")
        # It's disabled - not too useful
        # self._stress_frame.pack(expand=1, side=tk.LEFT)
        self._stress_label = ttk.Label(self._stress_frame, text="Stress: ")
        self._stress_label.pack(side=tk.LEFT)
        self._check_on_image = tk.PhotoImage(data=SELECTED_THEME["check_on"])
        self._check_off_image = tk.PhotoImage(data=SELECTED_THEME["check_off"])
        self._checkbutton = tk.Checkbutton(self._stress_frame, variable=self._stress, onvalue=1,
                                           offvalue=0, image=self._check_off_image, selectimage=self._check_on_image,
                                           indicatoron=0, borderwidth=0, highlightthickness=0, relief=tk.FLAT,
                                           highlightcolor="red", overrelief=tk.FLAT, offrelief=tk.FLAT,
                                           background=SELECTED_THEME["light_frame_background"], takefocus=0,
                                           cursor="hand2")
        self._checkbutton.pack(side=tk.LEFT)

        # Change view frame button - from continuous view to 0-1 view
        self._view_frame = ttk.Frame(self._frame, style="Light.TFrame")
        self._view_frame.pack(expand=1, side=tk.LEFT)
        self._view_entry = ttk.Entry(self._view_frame, textvariable=self._threshold)
        self._view_entry.pack(side=tk.LEFT)
        self._view_btn = ttk.Button(self._view_frame, text="Change View", command=self._change_view,
                                    style="RoundedButtonLight.TButton", cursor="hand2")
        self._view_btn.pack(side=tk.LEFT)

        # Accuracy view frame
        self._accuracy_frame = ttk.Frame(self._frame, style="Light.TFrame")
        # It's disabled, not too useful
        # self._accuracy_frame.pack(expand=1, side=tk.LEFT)
        self._accuracy_hint = ttk.Label(self._accuracy_frame, text="Accuracy: ")
        self._accuracy_hint.pack(side=tk.LEFT)
        self._accuracy_label = ttk.Label(self._accuracy_frame, textvariable=self._accuracy)
        self._accuracy_label.pack(side=tk.LEFT)

        # Open Stroop Test and Quiz Test
        stroop_test.StroopTest(master=self._top_level)
        quiz_test.QuizTest(master=self._top_level)

        # There will be saved all data to plot
        self._predictions_data = []
        self._timestamps = []

        # Configuring the plot
        self._figure = Figure(figsize=(13, 7), dpi=100)
        self._axis = self._figure.add_subplot(1, 1, 1)
        self._axis.set_title("Prediction")
        self._axis.set_ylim((-0.1, 1.1))
        self._axis.set_yticks([0, 1])
        self._axis.set_yticklabels([0, 1])
        self._x_data = [x for x in range(4)]
        self._axis.set_xticks([i for i in range(0, len(self._x_data), 1)])
        self._axis.set_xlim((self._x_data[0], self._x_data[-1]))
        self._text = self._axis.text(0.5, 1.05, "Mean: 0", bbox=dict(facecolor='gray', alpha=0.2))

        # This line is mandatory to animate the plot
        self._predictions_line = self._axis.plot([], [], label='Stress Level')[0]
        self._axis.legend()

        self._canvas = FigureCanvasTkAgg(self._figure, self._top_level)
        self._canvas.get_tk_widget().pack(expand=1, fill=tk.BOTH)

        # Properties for thread management
        self._is_destroyed = False
        self._master_thread = None
        self._run_signal = threading.Event()  # signal to control master thread finish
        self._run_signal.set()
        self._prediction_queue = queue.Queue()

        # Support property
        self._after_job = None  # for gathering new prediction
        self._after_job2 = None  # for waiting thread finish

        # self._counter = 1

    def _change_view(self):
        """
        This method change the boolean that controls the showed view
        """
        self._threshold_view = not self._threshold_view

    @property
    def top_level(self):
        return self._top_level

    def _handle_close(self):
        if askokcancel("QUIT", "Do you really wish to quit?"):
            self._close()

    def _close(self):
        """
        This method handle the closing of the window
        """
        self._run_signal.clear()  # say to 'master_thread' to stop the execution
        if self._master_thread.is_alive():
            # If the thread is not closed we will retry after 50 ms
            self._after_job2 = self._top_level.after(50, self._close)
        else:
            # If here, the thread is terminated
            self._top_level.destroy()
            self._is_destroyed = True
            self._top_level.after_cancel(self._after_job2)
            self._after_job2 = None

    @property
    def is_destroyed(self):
        return self._is_destroyed

    def get_prediction(self):
        """
        This method is the main animation method, it tries to get a prediction from the queue: if there is one it will
        updates the plot.
        """
        if not self._is_destroyed:
            try:
                # Get the last prediction
                last_pred = self._prediction_queue.get(block=False)

                # Each prediction has the form of [timestamps, predictions]
                self._timestamps += last_pred[0]
                self._predictions_data += last_pred[1]

                if len(self._predictions_data) > 120:
                    self._predictions_data = self._predictions_data[4:]
                    self._timestamps = self._timestamps[4:]

                # In 'tmp_data' there will be predictions to which are applied the threshold function
                tmp_data = [1 if x > self._threshold.get() else 0 for x in self._predictions_data]

                # Filter - Ignore this part
                # IN_WHAT = 7
                # HOW_MUCH = 3
                # if len(tmp_data) > IN_WHAT:
                #     if tmp_data[-1] != 1:
                #         value = 0
                #         if tmp_data[-IN_WHAT:].count(1) > HOW_MUCH:
                #             value = 1
                #         tmp_data[-1] = value

                # Updating Accuracy
                current_target = self._stress.get()
                # Let's count how many threshold predictions (in 'tmp_data') are correct
                s = 0
                for element in tmp_data:
                    if element == current_target:
                        s += 1
                # Let's compute the accuracy
                new_acc = round(s / len(tmp_data), 2)
                # Let's compute a mean with the previous accuracy
                if self._prec_accuracy != -1:
                    new_acc = (new_acc + self._prec_accuracy) / 2
                self._accuracy.set(new_acc)
                self._prec_accuracy = new_acc

                # Let's see if show threshold data
                if self._threshold_view:
                    self._predictions_data = tmp_data

                # Let's show the mean of the predictions showed on the plot
                mean = float(np.mean(self._predictions_data))
                mean = round(mean, 2)
                text = "Mean: " + str(mean)
                self._text.set_text(text)

                # Let's take all data to plot but only 4-multiples to show ticks
                self._x_data = []
                x_ticks_data = []
                x_labels_data = []
                for i in range(len(self._predictions_data)):
                    self._x_data.append(i)
                    if i % 4 == 0:
                        x_ticks_data.append(i)
                        x_labels_data.append(self._timestamps[i])
                self._axis.set_xticks(x_ticks_data)
                self._axis.set_xticklabels(x_labels_data, rotation=30)
                self._axis.set_xlim(self._x_data[0], self._x_data[-1])
                self._predictions_line.set_data(self._x_data, self._predictions_data)
                self._canvas.draw()

            except queue.Empty:
                pass

            self._after_job = self._top_level.after(100, self.get_prediction)
        else:
            self._top_level.after_cancel(self._after_job)
            self._after_job = None

    def start_prediction(self):
        """
        This method start the update prediction loop
        """
        # We want to pass to thread only the Shimmer3 GSR+
        shimmer_to_pass = []
        for shimmer in self._shimmers:
            if shimmer.shimmer_type == util.SHIMMER_BA or shimmer.shimmer_type == util.SHIMMER_IMU \
                    or shimmer.shimmer_type == util.SHIMMER_ExG_0 or shimmer.shimmer_type == util.SHIMMER_ExG_1:
                pass
            else:
                shimmer_to_pass.append(shimmer)

        # Starting the thread that reads from Shimmers
        self._master_thread = threading.Thread(
            daemon=False,
            target=master_thread_implementation.master_thread_implementation,
            args=(shimmer_to_pass, self._run_signal, self._prediction_queue, self._model)
        )

        self._master_thread.start()

        self._after_job = self._top_level.after(100, self.get_prediction)
