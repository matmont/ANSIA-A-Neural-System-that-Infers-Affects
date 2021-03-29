import pickle
import tkinter as tk
from tkinter import ttk, StringVar, IntVar, DoubleVar
from tkinter.messagebox import showinfo, showerror

from gui import util as util_gui
from gui.task_popup import TaskPopup
from shimmer import util as util_shimmer

SELECTED_THEME = util_gui.DRIBBBLE_THEME


class SensorTabContent(ttk.Frame):
    """
    SensorTabContent represents the general tab for a Shimmer device (tab of the Notebook)
    """

    def __init__(self, master=None, sensor=None, available_ports=None, last_com_ports=None):
        """
        Constructor

        :param master: the parent window
        :param sensor: the Shimmer3 object that represents the device of this tab
        :param available_ports: list of all available COM ports in that host
        :param last_com_ports: last COM ports used for a successfully connection with the Shimmer3 devices
        """
        super(SensorTabContent, self).__init__(master=master, style="Tab.TFrame")

        self._sensor = sensor
        self._available_ports = available_ports
        self._last_com_ports = last_com_ports

        self._available_sensors = self._sensor.get_available_sensors()
        self._selected_sensors = {}
        for sensor in self._available_sensors:
            value = 0
            if sensor["name"] in self._sensor.enabled_sensors:
                value = 1
            self._selected_sensors[sensor["name"]] = IntVar(value=value)

        # DYNAMIC VARIABLES for input widgets
        self._selected_port = StringVar(value=self._last_com_ports[self._sensor.shimmer_type])
        self._sampling_rate = DoubleVar(value=self._sensor.sampling_rate)

        # Checkbox styling
        self._check_on_image = tk.PhotoImage(data=SELECTED_THEME["check_on"])
        self._check_off_image = tk.PhotoImage(data=SELECTED_THEME["check_off"])

        self._not_connected_main_frame = self._not_yet_connected_page()
        self._connected_main_frame = self._connected_page()
        self._current_view = "Not Connected"

        # Let's show the correct view
        if self._sensor.current_state != util_shimmer.IDLE \
                and self._sensor.current_state != util_shimmer.SD_LOGGING:
            self._connected_main_frame.pack(expand=1, fill=tk.BOTH)
            self._current_view = "Connected"
        else:
            self._not_connected_main_frame.pack(expand=1, fill=tk.BOTH)

    def _not_yet_connected_page(self):
        """
        Implement the "NotYetConnected" view. This view is shown when
        the Shimmer device is not connected yet.

        :return: the main Frame of the view
        """
        main_frame = ttk.Frame(self, style="Tab.TFrame")
        form_frame = ttk.Frame(main_frame, style="Tab.TFrame")  # useful for center widgets
        form_frame.pack(expand=1)

        label_selection = ttk.Label(form_frame, text="Select COM Port: ")
        label_selection.pack(pady=(0, 2))
        self._selection = ttk.Combobox(form_frame, cursor="hand2", values=self._available_ports, state="readonly",
                                       justify=tk.LEFT, style="CustomCombobox.TCombobox",
                                       textvariable=self._selected_port)

        self._selection.pack()

        label_warning = ttk.Label(form_frame, style="Warning.TLabel",
                                  text="Be sure that you choose the correct \nport for the correct sensor!")
        label_warning.pack(pady=(1, 0))
        self._label_hint = ttk.Label(form_frame, text="discover how", style="Link.Small.TLabel", cursor="hand2")
        self._label_hint.pack(pady=(0, 5))
        # Customizing for 'over' event
        self._label_hint.bind("<Enter>", lambda event: self._configure_text_window(
            foreground=SELECTED_THEME["link_over_text_color"],
        ))
        # Customizing for 'leave' event (normal)
        self._label_hint.bind("<Leave>", lambda event: self._configure_text_window(
            foreground=SELECTED_THEME["link_normal_text_color"],
        ))
        # Customizing for 'click-in' event
        self._label_hint.bind("<Button-1>", lambda event: self._configure_text_window(
            foreground=SELECTED_THEME["link_clicking_text_color"]
        ))
        self._label_hint.bind("<ButtonRelease-1>", lambda event: showinfo("How to check COM Ports",
                                                                          "Go to: START -> BLUETOOTH DEVICES -> "
                                                                          "DEVICES AND "
                                                                          "PRINTERS.\nNow search for your DEVICE (e.g. "
                                                                          "Shimmer3-XXXX), "
                                                                          "right click on it: PROPERTIES.\nClick on "
                                                                          "the HARDWARE tab "
                                                                          " and you'll find the COM port."))
        connect_button = ttk.Button(form_frame, text="Connect", command=self._connect, cursor="hand2",
                                    style="RoundedButtonLight.TButton")
        connect_button.pack(pady=5, ipady=1)
        return main_frame

    def _connected_page(self):
        """
        Implement the "Connected" view. That view is shown where
        the Shimmer device is connected.

        :return: the main Frame of the view
        """
        # Main Frame
        main_frame = ttk.Frame(self, style="Tab.TFrame")
        main_frame.rowconfigure(0, weight=2)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        # General Options Frame
        left_frame = ttk.Frame(main_frame, style="Tab.TFrame")
        left_frame.grid(row=0, column=0, sticky="nwes")

        # Frequency Management
        frequency_frame = ttk.Frame(left_frame, style="Tab.TFrame")
        frequency_frame.pack(expand=1, side=tk.TOP)
        frequency_entry_label = ttk.Label(frequency_frame, text="Sampling Rate: (Hz)")
        frequency_entry_label.pack(expand=1)
        frequency_entry = ttk.Entry(frequency_frame, textvariable=self._sampling_rate)
        frequency_entry.pack(expand=1)
        frequency_entry.bind("<Leave>", self._rounding_sampling_rate)
        frequency_entry.bind("<FocusOut>", self._rounding_sampling_rate)  # little bit defensive ?

        specialized_frame = self._specialized_frame(left_frame)
        if specialized_frame is not None:
            specialized_frame.pack(expand=1, side=tk.TOP)

        # Sensors Options Frame
        enabled_sensors_frame = ttk.Frame(main_frame, style="Tab.TFrame")
        enabled_sensors_frame.grid(row=0, column=1, sticky="nwes")
        enabled_sensors_frame.rowconfigure(0, weight=1)
        enabled_sensors_frame.rowconfigure(1, weight=5)
        enabled_sensors_frame.columnconfigure(0, weight=1)

        enabled_sensors_label = ttk.Label(enabled_sensors_frame, text="Enabled Sensors: ")
        enabled_sensors_label.grid(row=0, column=0)

        enabled_sensors_grid = ttk.Frame(enabled_sensors_frame, style="Tab.TFrame")
        enabled_sensors_grid.grid(row=1, column=0, sticky="nwes")

        # Showing all sensors, to enable/disable them
        i = 0
        j = 0
        for sensor in self._available_sensors:
            enabled_sensors_grid.rowconfigure(i, weight=1)
            enabled_sensors_grid.columnconfigure(j, weight=1)
            sensor_frame = ttk.Frame(enabled_sensors_grid, style="Tab.TFrame")
            sensor_frame.grid(row=i, column=j)

            sensor_name = sensor["name"]
            label = ttk.Label(sensor_frame, text=sensor_name, style="Light.TLabel")
            label.grid(row=0, column=0)
            checkbutton = tk.Checkbutton(sensor_frame, variable=self._selected_sensors[sensor["name"]], onvalue=1,
                                         offvalue=0, image=self._check_off_image, selectimage=self._check_on_image,
                                         indicatoron=0, borderwidth=0, highlightthickness=0, relief=tk.FLAT,
                                         highlightcolor="red", overrelief=tk.FLAT, offrelief=tk.FLAT,
                                         background=SELECTED_THEME["light_frame_background"], takefocus=0,
                                         cursor="hand2")
            checkbutton.grid(row=0, column=1)
            j += 1
            if j == 3:
                j = 0
                i += 1

        # Read/Write All Properties
        self._read_write_all_properties_frame = ttk.Frame(main_frame, style="Tab.TFrame")
        self._read_write_all_properties_frame.grid(row=1, column=0, columnspan=2)
        self._read_all_properties_btn = ttk.Button(self._read_write_all_properties_frame, text="Read Properties",
                                                   command=self.update_all, style="RoundedButtonLight.TButton")
        self._read_all_properties_btn.grid(row=0, column=0, padx=20)
        self._write_all_properties_btn = ttk.Button(self._read_write_all_properties_frame, text="Write Properties",
                                                    command=self.write_all, style="RoundedButtonLight.TButton")
        self._write_all_properties_btn.grid(row=0, column=1, padx=20)

        return main_frame

    def _connect(self):
        """
        This method is the callback linked to the button "Connect". It use 'func_connect'
        to implement the connection.
        """
        if self._selected_port.get() is not None and self._selected_port.get() != "":
            popup = TaskPopup(master=self, func=self._func_connect, args=())
            popup.start()
            self.wait_window(popup.top_level)
            if popup.result:
                self.update_all()
            else:
                showerror("ERROR", "Something went wrong during connection")
        else:
            showerror("ERROR", "You have to choose a COM port before!")

        # DEBUG -> only switch
        # self._switch_current_view()

    def _func_connect(self):
        """
        'func_connect' implement the connection with the Shimmer3 device.

        :return: True in case of successfully operation, False otherwise
        """
        if self._sensor.connect(self._selected_port.get(), write_rtc=True, update_all_properties=True,
                                reset_sensors=False):
            # Update Last Port File
            self._last_com_ports[self._sensor.shimmer_type] = self._selected_port.get()
            file = open('last_com_ports.pkl', 'wb')
            pickle.dump(self._last_com_ports, file)
            file.close()
            return True
        else:
            return False

    def _switch_current_view(self):
        """
        This method switch between the "NotYetConnected" page and the "Connected" page.
        """
        if self._current_view == "Not Connected":
            self._not_connected_main_frame.pack_forget()
            self._connected_main_frame.pack(expand=1, fill=tk.BOTH)
            self._current_view = "Connected"
        else:
            self._connected_main_frame.pack_forget()
            self._not_connected_main_frame.pack(expand=1, fill=tk.BOTH)
            self._current_view = "Not Connected"

    def _configure_text_window(self, **kwargs):
        """
        Auxiliary function to customize a widget.

        :param kwargs: list of params of customization
        """
        for avp in kwargs.items():
            attrib, value = avp
            self._label_hint[attrib] = value

    def update_all(self, show_info=True):
        """
        This method update the UI with info from the device.

        :param show_info: show a modal window that notifies the updating
        :type show_info: bool
        """
        if self._sensor.current_state == util_shimmer.BT_CONNECTED:
            self._selected_port.set(self._sensor.com_port)

            self._sampling_rate.set(self._sensor.sampling_rate)

            for sensor in self._available_sensors:
                value = 0
                if sensor["name"] in self._sensor.enabled_sensors:
                    value = 1
                self._selected_sensors[sensor["name"]].set(value)

            # Switch View
            if (self._current_view == "Not Connected" and self._sensor.current_state == util_shimmer.BT_CONNECTED) or (
                    self._current_view == "Connected" and self._sensor.current_state == util_shimmer.IDLE):
                self._switch_current_view()

            res = self._specialized_update_all()
            if res:
                # Notify the end of update
                if show_info:
                    showinfo("UPDATE", "All properties are succesfully readed!")
            else:
                showerror("ERROR", "Something went wrong during reading...")

        else:
            if self._current_view == "Connected":
                self._switch_current_view()

    # noinspection PyUnusedLocal
    def _rounding_sampling_rate(self, event):
        """
        This method rounds the sampling rate to show the correct configured sampling rate (that's
        probably different from the sampling rate requested, consider to read documentation of the
        LogAndStream firmware on Shimmer3 website)

        :param event: the Event of the widget
        """
        if self._sampling_rate.get() != 0:
            self._sampling_rate.set(round(32768.0 / round(32768.0 / self._sampling_rate.get()), 2))

    def update_sensor(self, sensor):
        """
        This method update the 'sensor' object linked to this tab. It is useful in case
        of deserialization.

        :param sensor: the new Shimmer3 object linked to the tab
        """
        self._sensor = sensor
        self.update_all(show_info=False)

    def _specialized_func_write_all(self):
        """
        This method should be override on sub-classes to specify some additional, specific, operations.
        :return: True in case of successfully operation, False otherwise
        """
        return True

    def _func_write_all(self):
        """
        This method implements the operations for writing settings on the Shimmer3 device.

        :return: True in case of successfully operation, False otherwise
        """
        if not self._sensor.set_sampling_rate(self._sampling_rate.get()):
            return False

        # Enabling selected sensors
        sensors_to_enable = []
        for sensor in self._available_sensors:
            if self._selected_sensors[sensor["name"]].get():
                sensors_to_enable.append(sensor)
        if not self._sensor.set_enabled_sensors(*sensors_to_enable):
            return False

        # This is a custom choice, for simplicity
        if not self._sensor.set_wide_acc_range(util_shimmer.WIDE_ACC_RANGE_2g):
            return False

        # This is a custom choice, for simplicity
        if not self._sensor.set_gyro_range(1):
            return False

        # Call all the specialized operation (useful for sub-classes)
        res = self._specialized_func_write_all()

        return res

    def write_all(self):
        """
        Callback linked to 'Write' button click. It use 'TaskPopup' to write
        all settings to the Shimmer3 device.
        """
        if self._sensor.current_state == util_shimmer.BT_CONNECTED:
            popup = TaskPopup(master=self, func=self._func_write_all, args=())
            popup.start()
            self.wait_window(popup.top_level)
            if popup.result:
                showinfo("WRITE", "All properties are written to the Shimmer.")
                self.update_all(show_info=False)
            else:
                showerror("ERROR", "Something went wrong...")
        else:
            showerror("ERROR", "The Shimmer is not connected...")

    def _specialized_update_all(self):
        """
        This method should be override on sub-classes to specify some additional, specific, operations.
        :return: True in case of successfully operation, False otherwise
        """
        return True

    def _specialized_frame(self, master):
        """
        This method should be override on sub-classes to implements eventual specialized settings' frame
        :param master: the parent window
        :return: the specialized frame
        """
        return None
