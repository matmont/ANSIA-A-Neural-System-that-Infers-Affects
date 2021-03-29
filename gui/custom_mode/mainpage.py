import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import showerror, showinfo
from tkinter.filedialog import askdirectory

from gui.custom_mode.sensors_tab_menu import SensorsTabMenu
from gui.task_popup import TaskPopup
from gui.custom_mode.plot_screen import PlotsScreen

from shimmer import util as util_shimmer
from shimmer.shimmer import Shimmer3

import json

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720


class MainPage(ttk.Frame):
    """
    MainPage is the home window of the Experimental/Custom mode.
    """
    def __init__(self, master=None, sensors=None, available_ports=None, last_com_ports=None):
        """
        Constructor

        :param master: the parent window
        :param sensors: list of Shimmer3 objects. Each object represents a particular Shimmer3 devices
        :param available_ports: list of all available COM ports in that host
        :param last_com_ports: last COM ports used for a successfully connection with the Shimmer3 devices
        """
        super(MainPage, self).__init__(master=master)

        # Retrieving the reference to the master window, the root
        self._root = master
        # Settings window's size and position - Center the window
        position_from_left = int(self._root.winfo_screenwidth() / 2 - WINDOW_WIDTH / 2)
        position_from_top = int(self._root.winfo_screenheight() / 2 - WINDOW_HEIGHT / 2)
        self._root.geometry("{}x{}+{}+{}".format(WINDOW_WIDTH, WINDOW_HEIGHT, position_from_left, position_from_top))
        self._root.resizable(True, True)
        self._root.minsize(WINDOW_WIDTH - 300, WINDOW_HEIGHT - 100)

        self._sensors = sensors
        self._available_ports = available_ports
        self._last_com_ports = last_com_ports

        # Configuring the Grid Layout
        self.rowconfigure(0, weight=2, minsize=480)
        self.rowconfigure(1, weight=1, minsize=240)
        self.columnconfigure(0, weight=1, minsize=800)

        """
            Layout:
        
            +---------------------+
            |                     |
            |     sensors tab     |
            |                     |  
            ----------------------+                     
            |                     |
            | save - load - stream|
            |                     |
            +---------------------+
        """

        # Upper Frame - Signals Tab Menu Region
        upper_frame = ttk.Frame(self)

        # Custom Widget
        self._sensors_tab = SensorsTabMenu(upper_frame, sensors=self._sensors,
                                           available_ports=self._available_ports, last_com_ports=self._last_com_ports)
        self._sensors_tab.pack(expand=1, fill=tk.BOTH)

        upper_frame.grid(row=0, column=0, sticky="nwes")

        # Lower Frame - Buttons Region
        lower_frame = ttk.Frame(self)
        lower_frame.rowconfigure(0, weight=1)
        lower_frame.columnconfigure(0, weight=1)
        lower_frame.columnconfigure(1, weight=1)
        lower_frame.bind("<Configure>", self.on_resize)

        # Load/Save Buttons Frame
        self._load_save_btn_frame = ttk.Frame(lower_frame, width=1246 / 2)
        self._load_save_btn_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=1, padx=(2, 2), pady=2)

        # Save configuration button
        self._btn_save = ttk.Button(self._load_save_btn_frame, text="Save Configuration", cursor="hand2",
                                    command=self._save_config, style="RoundedButtonDark.TButton")
        self._btn_save.pack(expand=1, side=tk.LEFT)

        # Load configuration button
        self._btn_load = ttk.Button(self._load_save_btn_frame, text="Load Configuration", cursor="hand2",
                                    command=self._load_config, style="RoundedButtonDark.TButton")
        self._btn_load.pack(expand=1, side=tk.LEFT)

        # Stream Btn Frame
        self._stream_btn_frame = ttk.Frame(lower_frame, width=1246 / 2)
        self._stream_btn_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=1, padx=(0, 2), pady=2)
        # Stream button
        self._btn_stream = ttk.Button(self._stream_btn_frame, text="STREAM", cursor="hand2",
                                      command=self._start_stream,
                                      style="BigLabel.RoundedButtonDark.TButton")
        self._btn_stream.pack(expand=1, fill=tk.BOTH, pady=50, padx=100)

        lower_frame.grid(row=1, column=0, sticky="nwes", padx=15, pady=(0, 15))

    def on_resize(self, event):
        """
        Make sure that lower frames stay centered

        :param event: the resize Event
        """
        self._load_save_btn_frame.config(width=event.width / 2)
        self._stream_btn_frame.config(width=event.width / 2)

    def _start_stream(self):
        """
        Strat the bluetooth Streaming between Shimmer3 devices and PC Host. This method
        will open PlotScreen for the real time data visualization.
        """

        # Check that there is at least one Shimmer connected
        at_least_one_connected = False
        for sensor in self._sensors:
            if sensor.current_state is util_shimmer.BT_CONNECTED:
                at_least_one_connected = True
                break

        if at_least_one_connected:
            # Let the user choose a location for CSV files saving
            filename = askdirectory()

            # Open the PlotsScreen page
            plots_screen = PlotsScreen(master=self, sensors=self._sensors, filename=filename)
            # This call hide the MainPage
            self._root.withdraw()

            plots_screen.start_streaming()

            # This call block the execution of that flow of code
            self.wait_window(plots_screen.top_level)
            # Show again the MainPage
            self._root.update()
            self._root.deiconify()
        else:
            showerror("ERROR", "At least 1 sensor has to be connected!")

    def update_all(self):
        """
        Call 'update_all' method of the object SensorsTabMenu.
        """
        self._sensors_tab.update_all()

    def _save_config(self):
        """
        Save the current configuration of Sensors.
        """

        # Checking if there is at least one sensor connected
        at_least_one_connected = False
        for sensor in self._sensors:
            if sensor.current_state == util_shimmer.BT_CONNECTED:
                at_least_one_connected = True
                break

        # We save configuration only if there is at least one sensor connected
        if at_least_one_connected:
            # Let the user choose where to save the .json file
            file = filedialog.asksaveasfile(defaultextension=".json", filetypes=[("JSON File", ".json")])
            if file is not None:
                # TODO: probably it's better to put that line into a TaskPopup
                json.dump(self._sensors, file, indent=4, default=Shimmer3.encode_to_json)
                showinfo("SAVED", "Your configuration is now saved on your pc.")
            else:
                showerror("ERROR", "Something went wrong during saving...")
        else:
            showinfo("WARNING", "No sensor is connected: it doesn't have much sense to save this configuration!")

    def _load_config(self):
        # Let the user choose from what file load the configuration
        file = filedialog.askopenfile()
        if file is not None:
            popup = TaskPopup(master=self, func=self._decoding_function, args=(file, self._sensors))
            popup.start()
            self.wait_window(popup.top_level)
            self._sensors = popup.result
            # That line call 'update_all' for each Shimmer type (in that way the UI remain
            # consistent with the sensors data, that we have just retrieved)
            self._sensors_tab.update_sensors(self._sensors)
            showinfo("LOAD", "Configuration loaded succesfully!")
        else:
            showerror("ERROR", "Something went wrong during loading...")

    @staticmethod
    def _decoding_function(file, *sensors):
        # First, we want to disconnect all Shimmers
        for sensor in sensors:
            sensor.disconnect()
        # Retrieving data from file -> check 'decode_from_json': after the data reading, some info should be
        # sent to Shimmer device, over bluetooth (after connection). This occurs if the saved sensor was connected.
        sensors = json.loads(file.read(), object_hook=Shimmer3.decode_from_json)
        return sensors
