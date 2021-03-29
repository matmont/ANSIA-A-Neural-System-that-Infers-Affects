import queue
import threading
import tkinter as tk
from tkinter.messagebox import askokcancel

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gui.custom_mode import streaming_session
from shimmer import util

matplotlib.use("TkAgg")


# source -> https://stackoverflow.com/questions/3229419/how-to-pretty-print-nested-dictionaries
# Pretty printer for DICTs
def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent + 1)
        else:
            print('\t' * (indent + 1) + str(value))


class PlotsScreen:
    """
    PlotsScreen implements the real time plotting of the data from Shimmer devices
    """

    def __init__(self, master=None, sensors=None, filename=None):
        """
        Constructor

        :param master: the parent window
        :param sensors: list of Shimmer3 objects. Each object represents a particular Shimmer3 devices
        :param filename: the path of the location chosen from the user
        """
        self._master = master
        self._sensors = sensors
        self._filename = filename
        self._enabled_sensors = []
        for sensor in self._sensors:
            if sensor.current_state == util.BT_CONNECTED:
                self._enabled_sensors.append(sensor)

        self._top_level = tk.Toplevel(master=self._master)
        self._top_level.title("PLOTS")
        self._top_level.resizable(False, False)
        # This line allows to manage the closing of the window
        self._top_level.protocol("WM_DELETE_WINDOW", self._handle_close)
        pad = 3  # padding -> how much space between the end of the screen
        self._top_level.geometry("{0}x{1}+0+0".format(
            self._top_level.winfo_screenwidth() - pad, self._top_level.winfo_screenheight() - pad))
        self._figure = Figure(figsize=(20, 9), dpi=100)
        self._figure.subplots_adjust(hspace=0.5)
        self._axes = {}

        # Drawing a subplot for each Shimmer3 device
        index = 0
        for sensor in self._sensors:
            ax = self._figure.add_subplot(3, 2, index + 1)
            ax.set_title(sensor.shimmer_type)
            index += 1
            self._axes[sensor.shimmer_type] = ax

        # Initialisation of the lines. For each device, there is one line for each channel enabled
        # within the device
        self._lines = {}
        for sensor in self._enabled_sensors:
            self._lines[sensor.shimmer_type] = {}
            for channel in sensor.channels:
                self._lines[sensor.shimmer_type][channel] = self._axes[sensor.shimmer_type].plot([], [], label=channel)
            self._axes[sensor.shimmer_type].legend(loc='lower left')

        self._canvas = FigureCanvasTkAgg(self._figure, self._top_level)
        self._canvas.get_tk_widget().pack(expand=1, fill=tk.BOTH)

        # Current reads to show
        self._reads = {}
        self._timestamps = {}
        self._n_of_points = {}
        self._first_timestamp = {}
        for sensor in self._enabled_sensors:
            self._reads[sensor.shimmer_type] = {}
            for channel in sensor.channels:
                self._reads[sensor.shimmer_type][channel] = []

            self._timestamps[sensor.shimmer_type] = []
            # We want only the last 20 reads
            # Notice that not all the reads from the Shimmer are plotted
            # TODO: probably it's better to plot last X minutes or seconds
            self._n_of_points[sensor.shimmer_type] = 20
            self._first_timestamp[sensor.shimmer_type] = None

        # Stuff for the reading thread management
        self._is_destroyed = False
        self._streaming_session_THREAD = None
        self._run_signal = threading.Event()
        self._run_signal.set()
        self._queue = queue.Queue()

        # Other stuff
        self._after_job = None  # for updating data
        self._after_job2 = None  # for waiting the thread end

    @property
    def top_level(self):
        return self._top_level

    def update_data(self):
        """
        It retrieves the last reads and updates showed data.
        """

        if not self._is_destroyed:
            try:
                # Here we have at most one read for each enabled sensor
                last_read = self._queue.get(block=False)
                for sensor in self._enabled_sensors:
                    # We have to check if, for that device, there is a read
                    if last_read[sensor.shimmer_type] is not None:
                        read = last_read[sensor.shimmer_type]
                        # Format -> [synced timestamp (float), data]
                        time = read[0]
                        if self._first_timestamp[sensor.shimmer_type] is None:
                            self._first_timestamp[sensor.shimmer_type] = time

                        time = time - self._first_timestamp[sensor.shimmer_type]

                        channels_data = read[1:]
                        self._timestamps[sensor.shimmer_type].append(time)
                        # Eventually cut timestamps to the last X points
                        if len(self._timestamps[sensor.shimmer_type]) > self._n_of_points[sensor.shimmer_type]:
                            self._timestamps[sensor.shimmer_type] = self._timestamps[sensor.shimmer_type][
                                                                    -self._n_of_points[sensor.shimmer_type]:]

                        # Updating the graph minimum and maximum of the y axes
                        min_y = None
                        max_y = None
                        channels = sensor.channels
                        for i in range(len(channels)):
                            self._reads[sensor.shimmer_type][channels[i]].append(channels_data[i])
                            # Cut reads to the last X points
                            if len(self._reads[sensor.shimmer_type][channels[i]]) > self._n_of_points[
                                sensor.shimmer_type]:
                                self._reads[sensor.shimmer_type][channels[i]] = self._reads[sensor.shimmer_type][
                                                                                    channels[i]][-self._n_of_points[
                                    sensor.shimmer_type]:]

                            # Compute minimum and maximum for that channel
                            tmp_min_y = min(self._reads[sensor.shimmer_type][channels[i]])
                            tmp_max_y = max(self._reads[sensor.shimmer_type][channels[i]])
                            if min_y is None or min_y > tmp_min_y:
                                min_y = tmp_min_y
                            if max_y is None or max_y < tmp_max_y:
                                max_y = tmp_max_y

                        pad_y = int(abs(max_y - min_y) / 10)
                        self._axes[sensor.shimmer_type].set_ylim((min_y - pad_y, max_y + pad_y))
                        self._axes[sensor.shimmer_type].set_xlim((self._timestamps[sensor.shimmer_type][0] - 1,
                                                                  self._timestamps[sensor.shimmer_type][-1] + 1))

                        # Updating each line of each graph
                        for key, value in self._lines[sensor.shimmer_type].items():
                            if key == "X Boundaries" or key == "Y Boundaries":
                                # old implementation
                                pass
                            else:
                                value[0].set_data(self._timestamps[sensor.shimmer_type],
                                                  self._reads[sensor.shimmer_type][key])

                # Update the all canvas. This is required to achieve animation effect.
                self._canvas.draw()

            except queue.Empty:
                pass

            self._after_job = self._top_level.after(1, self.update_data)
        else:
            self._top_level.after_cancel(self._after_job)
            self._after_job = None

    def _handle_close(self):
        """
        This method manages the closing of the main window.
        """
        if askokcancel("QUIT", "Do you really wish to quit?"):
            self._close()

    def _close(self):
        """
        This is the method that makes all the stuff before the closing of the main window.
        """
        self._run_signal.clear()  # say to thread to stop
        if self._streaming_session_THREAD.is_alive():
            print("Thread has not finished yet...")
            self._after_job2 = self._top_level.after(50, self._close)
        else:
            self._top_level.destroy()
            self._is_destroyed = True
            self._top_level.after_cancel(self._after_job2)
            self._after_job2 = None

    @property
    def is_destroyed(self):
        return self._is_destroyed

    def start_streaming(self):
        """
        This method launches the 'streaming_session' thread. So it starts the streaming and so the plotting
        """
        self._streaming_session_THREAD = threading.Thread(
            daemon=False,
            target=streaming_session.streaming_session,
            args=(self._enabled_sensors, self._run_signal, self._queue, self._filename),
        )

        self._streaming_session_THREAD.start()

        # Call 'update_data' after 10 milliseconds
        self._after_job = self._top_level.after(10, self.update_data)
