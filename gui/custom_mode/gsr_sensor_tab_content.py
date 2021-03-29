from gui.custom_mode.sensor_tab_content import SensorTabContent

import tkinter as tk

from tkinter import StringVar
from tkinter import ttk

from shimmer import util


class GsrSensorTabContent(SensorTabContent):
    """
    GsrSensorTabContent is the specialization of a SensorTabContent for the Shimmer3 GSR+ device.
    """

    def __init__(self, master=None, sensor=None, available_ports=None, last_com_ports=None):
        """
        Constructor
        :param master: the parent window
        :param sensor: the object Shimmer3 that represents the Shimmer3 GSR+ device
        :param available_ports: list of all available COM ports in that host
        :param last_com_ports: last COM ports used for a successfully connection with the Shimmer3 devices
        """
        self._active_gsr_mu = StringVar(value=sensor.active_gsr_mu)
        super(GsrSensorTabContent, self).__init__(master=master, sensor=sensor, available_ports=available_ports,
                                                  last_com_ports=last_com_ports)

    def _specialized_frame(self, master):
        """
        Implement the specialized frame (bottom-left) of the sensor configuration's UI.

        :param master: the parent window
        :return: the specialized frame
        """
        frame = ttk.Frame(master, style="Tab.TFrame")
        # In the case of GSR+ we want to choose what Measurement Units it should be used
        # for the GSR sensor.
        # (mu = Measurement Unit)
        label_mu = ttk.Label(frame, text="GSR Measurement Unit: ")
        label_mu.pack(pady=(0, 2))
        selection = ttk.Combobox(frame, cursor="hand2", values=[util.GSR_SKIN_CONDUCTANCE, util.GSR_SKIN_RESISTANCE],
                                 state="readonly",
                                 justify=tk.LEFT, style="CustomCombobox.TCombobox",
                                 textvariable=self._active_gsr_mu)
        selection.pack()

        return frame

    def _specialized_func_write_all(self):
        """
        Add specialized writing operations at the default 'write_all'

        :return: True in case of successfully operation, False otherwise
        """
        # We want to set in AUTO mode the GSR range setting.
        # Read Shimmer3 GSR+ documentation on the Shimmer3 website for more info.
        if not self._sensor.set_gsr_range(4):
            return False

        if not self._sensor.set_active_gsr_mu(new_mu=self._active_gsr_mu.get()):
            return False

        return True

    def _specialized_update_all(self):
        """
        Add specialized reading operations at the default 'update_all'.

        :return: True in case of successfully operation, False otherwise
        """
        self._active_gsr_mu.set(self._sensor.active_gsr_mu)
        return True
