from tkinter import ttk

from gui.custom_mode import sensor_tab_content, gsr_sensor_tab_content, exg_sensor_tab_content
from shimmer import util


class SensorsTabMenu(ttk.Notebook):
    """
    'SensorTabMenu' implements the Notebook that stores tabs from all Shimmer3 devices.
    """
    def __init__(self, master=None, sensors=None, available_ports=None, last_com_ports=None):
        """
        Constructor

        :param master: the parent window
        :param sensors: list of Shimmer3 objects. Each object represents a particular Shimmer3 devices
        :param available_ports: list of all available COM ports in that host
        :param last_com_ports: last COM ports used for a successfully connection with the Shimmer3 devices
        """
        super(SensorsTabMenu, self).__init__(master=master)

        # Retrieve the list of sensors
        self._sensors = sensors

        # Get the window's size
        self._tab_menu_width = self.winfo_width()
        self._tab_menu_height = self.winfo_height()

        self._sensors_tabs = {}
        # Creating Tabs - for Shimmer3 GSR+ and Shimmer3 ExG we have
        # specialized Tab.
        for sensor in self._sensors:
            if sensor.shimmer_type == util.SHIMMER_GSRplus:
                sensor_tab = gsr_sensor_tab_content.GsrSensorTabContent(self, sensor=sensor,
                                                                        available_ports=available_ports,
                                                                        last_com_ports=last_com_ports)
            elif sensor.shimmer_type == util.SHIMMER_ExG_0 or sensor.shimmer_type == util.SHIMMER_ExG_1:
                sensor_tab = exg_sensor_tab_content.ExgSensorTabContent(self, sensor=sensor,
                                                                        available_ports=available_ports,
                                                                        last_com_ports=last_com_ports)
            else:
                sensor_tab = sensor_tab_content.SensorTabContent(self, sensor=sensor, available_ports=available_ports,
                                                                 last_com_ports=last_com_ports)

            self._sensors_tabs[sensor.shimmer_type] = sensor_tab

            # We have two type of ExG -> for simplicity we differentiate one from the other and set the first as
            # EMG and the second as ECG
            if sensor.shimmer_type == util.SHIMMER_ExG_0 or sensor.shimmer_type == util.SHIMMER_ExG_1:
                tab_title = "ExG"
            else:
                tab_title = sensor.shimmer_type
            # Adding Tab to the Notebook widget (it's the Tab Menu)
            self.add(sensor_tab, text=tab_title)

    def update_all(self):
        # Usually called from MainPage, it call 'update_all' on all different Shimmers
        for key, tab in self._sensors_tabs.items():
            tab.update_all(show_info=False)

    def update_sensors(self, sensors):
        # This function is needed because of the deserialization. It updates the sensors object
        self._sensors = sensors
        for sensor in self._sensors:
            self._sensors_tabs[sensor.shimmer_type].update_sensor(sensor)
