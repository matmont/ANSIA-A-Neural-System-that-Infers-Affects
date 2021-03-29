from gui.custom_mode.sensor_tab_content import SensorTabContent

import tkinter as tk

from tkinter import StringVar
from tkinter import ttk

from shimmer import util


class ExgSensorTabContent(SensorTabContent):
    """
    ExgSensorTabContent is the specialization of a SensorTabContent for the Shimmer3 ExG device.
    """

    def __init__(self, master=None, sensor=None, available_ports=None, last_com_ports=None):
        """
        Constructor

        :param master: the parent window
        :param sensor: the object Shimmer3 that represents the Shimmer3 ExG device
        :param available_ports: list of all available COM ports in that host
        :param last_com_ports: last COM ports used for a successfully connection with the Shimmer3 devices
        """
        self._active_purpose = StringVar(value=sensor.exg_purpose)
        super(ExgSensorTabContent, self).__init__(master=master, sensor=sensor, available_ports=available_ports,
                                                  last_com_ports=last_com_ports)

    def _specialized_frame(self, master):
        """
        Implement the specialized frame (bottom-left) of the sensor configuration's UI.

        :param master: the parent window
        :return: the specialized frame
        """
        frame = ttk.Frame(master, style="Tab.TFrame")
        # Purpose
        label_purpose = ttk.Label(frame, text="Purpose: ")
        label_purpose.pack(pady=(0, 2))
        selection = ttk.Combobox(frame, cursor="hand2",
                                 values=[util.ExG_ECG, util.ExG_EMG, util.ExG_RESP, util.ExG_TEST],
                                 state="readonly",
                                 justify=tk.LEFT, style="CustomCombobox.TCombobox",
                                 textvariable=self._active_purpose)
        selection.pack()
        selection.bind("<<ComboboxSelected>>", self._on_combobox_change)

        return frame

    def _specialized_update_all(self):
        """
        Add specialized reading operations at the default 'update_all'.

        :return: True in case of successfully operation, False otherwise
        """
        purpose = self._sensor.exg_purpose
        if purpose is not None:
            self._active_purpose.set(purpose)
        return True

    def _specialized_func_write_all(self):
        """
        Add specialized writing operations at the default 'write_all'

        :return: True in case of successfully operation, False otherwise
        """
        active = self._active_purpose.get()
        res = True
        if active == util.ExG_EMG:
            res = self._sensor.exg_send_emg_settings(util.ExG_GAIN_4)
        elif active == util.ExG_ECG:
            res = self._sensor.exg_send_ecg_settings(util.ExG_GAIN_12)
        elif active == util.ExG_RESP:
            res = self._sensor.exg_send_resp_settings()
        elif active == util.ExG_TEST:
            res = self._sensor.exg_send_exg_test_settings()
        return res

    def _on_combobox_change(self, event):
        """
        This function enable/disable ExG sensors based on what purposes is chosen.

        :param event: the change selection Event
        """
        selected = self._active_purpose.get()
        if selected == util.ExG_ECG or selected == util.ExG_TEST:
            self._selected_sensors[util.SENSOR_ExG1_24BIT["name"]].set(1)
            self._selected_sensors[util.SENSOR_ExG2_24BIT["name"]].set(1)
        elif selected == util.ExG_EMG:
            self._selected_sensors[util.SENSOR_ExG1_24BIT["name"]].set(1)
            self._selected_sensors[util.SENSOR_ExG2_24BIT["name"]].set(0)
