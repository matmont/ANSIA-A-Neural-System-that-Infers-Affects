import pickle
import tkinter as tk
from tkinter import StringVar, IntVar
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo

from gui import util as util_gui
from shimmer import util as util_shimmer
from gui.task_popup import TaskPopup
from gui.custom_mode import mainpage

SELECTED_THEME = util_gui.DRIBBBLE_THEME

WINDOW_WIDTH = 300
WINDOW_HEIGHT = 400


class SimultaneouslyConnections(ttk.Frame):
    """
    SimultaneouslyConnection is a widget that permits the connection of more than one
    device at time.
    """
    def __init__(self, master=None, sensors=None, available_ports=None, last_com_ports=None):
        """
        Constructor

        :param master: the parent window
        :param sensors: list of Shimmer3 objects. Each object represents a particular Shimmer3 devices
        :param available_ports: list of all available COM ports in that host
        :param last_com_ports: last COM ports used for a successfully connection with the Shimmer3 devices
        """
        super(SimultaneouslyConnections, self).__init__(master=master)

        self._root = master
        # Settings window's size and position - Center the window
        position_from_left = int(self._root.winfo_screenwidth() / 2 - WINDOW_WIDTH / 2)
        position_from_top = int(self._root.winfo_screenheight() / 2 - WINDOW_HEIGHT / 2)
        self._root.geometry("{}x{}+{}+{}".format(WINDOW_WIDTH, WINDOW_HEIGHT, position_from_left, position_from_top))
        # This window should not be resizable
        self._root.resizable(False, False)

        self._sensors = sensors
        self._available_ports = available_ports
        self._last_com_ports = last_com_ports

        self._main_frame = ttk.Frame(master, style="Light.TFrame")
        self._main_frame.pack(expand=1, fill=tk.BOTH, side=tk.LEFT)

        self._selected_ports = {}
        """This dict contains all the StringVar associated with Comboboxs. At the beginning, the value are taken from
        the 'last_com_ports' object retrieved at program launch. """
        for key, port in self._last_com_ports.items():
            self._selected_ports[key] = StringVar()
            if port is None:
                # The StringVar value is displayed in the Combobox, so we can't use None, instead we use an empty string
                self._selected_ports[key].set("")
            else:
                self._selected_ports[key].set(port)

        self._selected_sensors = {}
        """This dict contains all the IntVar associated with Checkboxes. For each shimmer, the type of it is used as a 
        key, and then this variable is the value: when 1 the shimmer is selected for connection, otherwise not 
        (and the value of the IntVar is 0)"""
        for sensor in sensors:
            self._selected_sensors[sensor.shimmer_type] = IntVar(value=0)

        # Checkbox styling: references to the different checkbutton images (for each state)
        self._check_on_image = tk.PhotoImage(data=SELECTED_THEME["check_on"])
        self._check_off_image = tk.PhotoImage(data=SELECTED_THEME["check_off"])

        # This frame is the main container of all widgets
        frame = ttk.Frame(master=self._main_frame, style="Light.TFrame")
        frame.pack(expand=1)

        # Take index of row: each sensor will be placed on a different row of the grid
        row = 0
        for sensor in self._sensors:
            frame.rowconfigure(row, pad=20)
            if sensor.shimmer_type == util_shimmer.SHIMMER_ExG_0 or sensor.shimmer_type == util_shimmer.SHIMMER_ExG_1:
                sensor_type_label = "ExG"
            else:
                sensor_type_label = sensor.shimmer_type

            label = ttk.Label(frame, text=sensor_type_label)
            label.grid(row=row, column=0, padx=5)

            combobox = ttk.Combobox(frame, values=self._available_ports, state="readonly",
                                    justify=tk.LEFT, style="CustomCombobox.TCombobox",
                                    textvariable=self._selected_ports[sensor.shimmer_type], cursor="hand2")
            combobox.grid(row=row, column=1, padx=5, pady=2)

            checkbutton = tk.Checkbutton(frame, variable=self._selected_sensors[sensor.shimmer_type], onvalue=1,
                                         offvalue=0, image=self._check_off_image, selectimage=self._check_on_image,
                                         indicatoron=0, borderwidth=0, highlightthickness=0, relief=tk.FLAT,
                                         highlightcolor="red", overrelief=tk.FLAT, offrelief=tk.FLAT,
                                         background=SELECTED_THEME["light_frame_background"], takefocus=0,
                                         cursor="hand2")
            checkbutton.grid(row=row, column=2, padx=5, pady=2)

            row += 1

        frame_buttons = ttk.Frame(self._main_frame, style="Light.TFrame")
        frame_buttons.pack(side=tk.LEFT, expand=1, pady=10, fill=tk.BOTH)

        button_connect = ttk.Button(frame_buttons, text="CONNECT", style="RoundedButtonLight.TButton",
                                    command=self._connect, cursor="hand2")
        button_connect.pack(side=tk.LEFT, expand=1)

        button_skip = ttk.Button(frame_buttons, text="SKIP", style="RoundedButtonLight.TButton", command=self._skip,
                                 cursor="hand2")
        button_skip.pack(side=tk.LEFT, expand=1)

    def _connect(self):
        """
        This function is the callback linked to the 'Connect' button.
        It use TaskPopup to implement the connections.
        """
        # Checking that the input is valid: e.g the user can't select a sensor without setting COM port
        sum_of_connect = 0
        for sensor in self._sensors:
            sensor_type = sensor.shimmer_type
            to_connect = self._selected_sensors[sensor_type].get()
            sum_of_connect += to_connect
            what_port = self._selected_ports[sensor_type].get()
            if to_connect:
                if what_port is None or what_port == "":
                    message = "You have not inserted the port for Shimmer3 " + str(sensor.shimmer_type)
                    showerror("ERROR", message)
                    return

        # If the user click 'Connect' with no sensor selected, it will be done a 'Skip'
        if sum_of_connect > 0:
            # At least one selected sensor
            popup = TaskPopup(master=self, func=self._func_connect, args=())
            popup.start()
            self.wait_window(popup.top_level)

            message = "CONNECTIONS REPORT: \n\n"
            # print the result
            for key, value in popup.result.items():
                if value:
                    aux = "Connected"
                else:
                    aux = "Not Connected"
                message += "    - " + key + ": " + aux + "\n"

            showinfo("REPORT", message)

        # Go to the main page
        self._main_frame.pack_forget()
        self._main_frame.destroy()

        main_page = mainpage.MainPage(master=self._root, sensors=self._sensors, available_ports=self._available_ports,
                                      last_com_ports=self._last_com_ports)
        # This update all sensor tabs content: after the connection we want to read some info from the
        # sensor (and also the connected status!)
        main_page.update_all()
        main_page.pack(expand=1, fill=tk.BOTH)
        self._root.geometry("1280x720")
        self._root.resizable(True, True)

    def _skip(self):
        """
        This function is the callback linked to the 'Skip' button.
        """
        # Go to the main page
        self._main_frame.pack_forget()
        self._main_frame.destroy()

        main_page = mainpage.MainPage(master=self._root, sensors=self._sensors, available_ports=self._available_ports,
                                      last_com_ports=self._last_com_ports)
        # In this case we don't need to call 'update_all' because no one change occured regarding sensors
        # self._main_page.update_all()
        main_page.pack(expand=1, fill=tk.BOTH)
        self._root.geometry("1280x720")
        self._root.resizable(True, True)

    def _func_connect(self):
        """
        This function is executed within TaskPopup: it is in charge of making all the connections with Shimmers.
            e.g.:
                {
                    IMU: True,\n
                    GSR+: False,
                }\n

            *(if only IMU and GSR+ are selected for connection)*

        :return: a dictionary containing the connections results for each type of Shimmer
        :rtype: dict
        """
        result = {}
        for sensor in self._sensors:
            # Retrieves sensor type, if it should be connected and on what port
            sensor_type = sensor.shimmer_type
            to_connect = self._selected_sensors[sensor_type].get()
            what_port = self._selected_ports[sensor_type].get()
            # If it should be connected we have to do something
            if to_connect:
                # This check is redundant (it has been done before in '_connect' function, that at a certain point
                # start the TaskPopup that use this function
                if what_port is not None and what_port != "":
                    # Connection to the Shimmer: we want to write the Real Time Clock (RTC), read all properties from
                    # the shimmer (and updating the relative Python object) but also resetting all sensors.
                    if sensor.connect(com_port=what_port, write_rtc=True, update_all_properties=True,
                                      reset_sensors=False):
                        # If here, the connection is done

                        # When a connection is succesfull, the software write the COM port used to the disk, for later
                        # uses
                        self._last_com_ports[sensor.shimmer_type] = what_port
                        file = open('last_com_ports.pkl', 'wb')
                        pickle.dump(self._last_com_ports, file)
                        file.close()

                        # Based on shimmer type, we could do something: e.g. i know that the IMU device should be
                        # used only for Wide Range Accelerometer -> we can enable it by default
                        # TODO: check for other Shimmer's type
                        if sensor_type == util_shimmer.SHIMMER_IMU:
                            sensor.set_enabled_sensors(util_shimmer.SENSOR_WIDE_RANGE_ACCELEROMETER)

                        # Success!
                        result[sensor.shimmer_type] = True
                    else:
                        # If here, the connection went wrong
                        result[sensor.shimmer_type] = False
                else:
                    # It should never be here
                    result[sensor.shimmer_type] = False

        return result
