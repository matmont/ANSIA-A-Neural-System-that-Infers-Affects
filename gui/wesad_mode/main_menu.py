import pickle
import tkinter as tk
from tkinter import StringVar
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror

from gui.task_popup import TaskPopup
from gui.wesad_mode import prediction_page
from gui.wesad_mode import tutorial_page
from shimmer import util as util_shimmer

WINDOW_HEIGHT = 500
WINDOW_WIDTH = 900


def _func_connect_gsr(shimmer, port):
    """
    This function prepares the Shimmer3 GSR+ device. It sets the sampling
    rate at 64 Hz and enable GSR and PPG sensors (with Skin Conductance measurement unit)

    :param shimmer: object Shimmer3 that represents the Shimmer3 GSR+
    :param port: port on which the Shimmer is connected
    :return: True in case of successfully operation, False otherwise
    """
    if shimmer.connect(com_port=port, write_rtc=True,
                       update_all_properties=True, reset_sensors=True):
        # After the connection we want to enable GSR and PPG
        if not shimmer.set_enabled_sensors(util_shimmer.SENSOR_GSR, util_shimmer.SENSOR_INT_EXP_ADC_CH13):
            return False
        # Set the sampling rate to 64 Hz
        if not shimmer.set_sampling_rate(64):  # actually will send 697.19 Hz
            return False
        # Set the GSR measurement unit to Skin Conductance (micro Siemens)
        if not shimmer.set_active_gsr_mu(util_shimmer.GSR_SKIN_CONDUCTANCE):
            return False
        return True
    else:
        return False


# def _func_connect_emg(shimmer, port):
#    print("Provo a connettere l'EMG sulla porta ", port)
#    if shimmer.connect(com_port=port, write_rtc=True,
#                       update_all_properties=True, reset_sensors=True):
#        # After the connection we want to enable ExG Chip 1 (EMG) - for now is only for debug
#        if not shimmer.set_enabled_sensors(util_shimmer.SENSOR_ExG1_24BIT, util_shimmer.SENSOR_ExG2_24BIT):
#            return False
#        # Set the sampling rate to 700 Hz
#        if not shimmer.set_sampling_rate(700):  # actually will send 697.19 Hz
#            return False
#        """
#        # Send the default settings for EMG measurement
#        if not shimmer.exg_send_emg_settings(util_shimmer.ExG_GAIN_12):
#            return False
#        """  # FOR DEBUG PURPOSES
#        if not shimmer.exg_send_exg_test_settings():
#            return False
#
#        return True
#    else:
#        return False
#
#
# def _func_connect_resp(shimmer, port):
#    if shimmer.connect(com_port=port, write_rtc=True,
#                       update_all_properties=True, reset_sensors=True):
#        # After the connection we want to enable ExG Chip 1 (EMG)
#        if not shimmer.set_enabled_sensors(util_shimmer.SENSOR_ExG1_24BIT, util_shimmer.SENSOR_ExG2_24BIT):
#            return False
#        # Set the sampling rate to 700 Hz
#        if not shimmer.set_sampling_rate(700):  # actually will send 697.19 Hz
#            return False
#        """
#        # Send the default settings for RESP measurement
#        if not shimmer.exg_send_resp_settings():
#            return False
#        """  # FOR DEBUG PURPOSES
#        if not shimmer.exg_send_exg_test_settings():
#            return False
#        return True
#    else:
#        return False


class MainMenu(ttk.Frame):
    """
    MainMenu implements the main menu of the WESAD mode
    """
    def __init__(self, master=None, shimmers=None, available_com_ports=None, last_com_ports=None, model=None):
        super(MainMenu, self).__init__(master, style="Dark.TFrame")
        self._root = master
        # Settings window's size and position - Center the window
        position_from_left = int(self._root.winfo_screenwidth() / 2 - WINDOW_WIDTH / 2)
        position_from_top = int(self._root.winfo_screenheight() / 2 - WINDOW_HEIGHT / 2)
        self._root.geometry("{}x{}+{}+{}".format(WINDOW_WIDTH, WINDOW_HEIGHT, position_from_left, position_from_top))
        self._root.resizable(True, True)
        self._root.minsize(900, 400)

        self._shimmers = shimmers
        self._available_com_ports = available_com_ports
        self._last_com_ports = last_com_ports
        self._model = model

        """
            Layout Idea:
            +--------------------------+
            |           gsr            |
            +--------------------------+
            |                          |
            |        connect all       |
            |                          |
            +--------------------------+                          
            |         predict          |
            +--------------------------+
        """

        self._selected_ports = {}
        for key, value in self._last_com_ports.items():
            # key -> Shimmer type | value -> last COM port used for that type
            self._selected_ports[key] = StringVar()
            if value is None:
                self._selected_ports[key].set("")
            else:
                self._selected_ports[key].set(value)

        shimmers_frame = ttk.Frame(master=self, style="Dark.TFrame")
        shimmers_frame.pack(expand=1, fill=tk.BOTH)

        # For now in _shimmers there is only the Shimmer3 GSR+...
        for shimmer in self._shimmers:
            if shimmer.shimmer_type == util_shimmer.SHIMMER_IMU or shimmer.shimmer_type == util_shimmer.SHIMMER_BA \
                    or shimmer.shimmer_type == util_shimmer.SHIMMER_ExG_0 or \
                    shimmer.shimmer_type == util_shimmer.SHIMMER_ExG_1:
                pass
            else:
                shimmer_frame = ttk.Frame(master=shimmers_frame, style="Dark.TFrame")
                shimmer_frame.pack(expand=1, side=tk.LEFT, padx=20)

                # Label
                shimmer_label = ttk.Label(master=shimmer_frame, text=shimmer.shimmer_type, style="DarkBack.Big.TLabel")
                shimmer_label.pack(expand=1, pady=15)

                # Combobox - for COM Port selection
                shimmer_com_port_frame = ttk.Frame(master=shimmer_frame, style="Dark.TFrame")
                shimmer_com_port_frame.pack(expand=1)

                shimmer_com_port_label = ttk.Label(master=shimmer_com_port_frame, text="COM Port",
                                                   style="DarkBack.TLabel")
                shimmer_com_port_label.pack(side=tk.TOP)

                shimmer_com_port_combobox = ttk.Combobox(master=shimmer_com_port_frame, cursor="hand2",
                                                         values=self._available_com_ports, state="readonly",
                                                         justify=tk.LEFT, style="CustomCombobox.TCombobox",
                                                         textvariable=self._selected_ports[shimmer.shimmer_type])
                shimmer_com_port_combobox.pack(expand=1)

        # In the 'connect_frame' we have Connect button and some hints
        connect_frame = ttk.Frame(master=self, style="Dark.TFrame")
        connect_frame.pack(expand=1, fill=tk.BOTH)
        tmp_frame = ttk.Frame(master=connect_frame, style="Dark.TFrame")
        tmp_frame.pack(expand=1)
        # Connect Button
        self._connect_button = ttk.Button(master=tmp_frame, text="Connect All",
                                          style="RoundedButtonDark.TButton", cursor="hand2", command=self._connect_all)
        self._connect_button.pack()

        # Disconnect Button
        self._disconnect_button = ttk.Button(master=tmp_frame, text="Disconnect All", style="RoundedButtonDark.TButton",
                                             cursor="hand2", command=self._disconnect_all)

        # COM Port Hint
        label_warning = ttk.Label(tmp_frame, style="DarkBack.Warning.TLabel",
                                  text="Be sure that you choose the correct \nport for the correct sensor!")
        label_warning.pack()
        # Hint label: this is a link that open a modal window in which the user can read an hint on how to choose
        # the correct COM port
        com_port_label_hint = ttk.Label(tmp_frame, text="discover how to get COM Port",
                                        style="DarkBack.Link.Small.TLabel",
                                        cursor="hand2")
        com_port_label_hint.pack(pady=(0, 5))
        # Style's link customization (e.g on mouse over, on mouse click, ...)
        com_port_label_hint.bind("<Enter>", )
        com_port_label_hint.bind("<Leave>", )
        com_port_label_hint.bind("<Button-1>", )
        # Open the modal window
        com_port_label_hint.bind("<ButtonRelease-1>", lambda event: showinfo("How to check COM Ports",
                                                                             "Go to: START -> BLUETOOTH DEVICES -> "
                                                                             "DEVICES AND "
                                                                             "PRINTERS.\nNow search for your DEVICE ("
                                                                             "e.g. "
                                                                             "Shimmer3-XXXX), "
                                                                             "right click on it: PROPERTIES.\nClick on "
                                                                             "the HARDWARE tab "
                                                                             " and you'll find the COM port."))

        # Tutorial
        tutorial_label = ttk.Label(tmp_frame, text="go back through tutorial", style="DarkBack.Link.Small.TLabel",
                                   cursor="hand2")
        tutorial_label.pack()
        tutorial_label.bind("<Enter>", )
        tutorial_label.bind("<Leave>", )
        tutorial_label.bind("<Button-1>", )
        tutorial_label.bind("<ButtonRelease-1>", self._go_through_tutorial)

        # Predict Frame
        predict_frame = ttk.Frame(master=self, style="Dark.TFrame")
        predict_frame.pack(expand=1, fill=tk.BOTH)

        # Predict Button
        predict_button = ttk.Button(master=predict_frame, text="PREDICT",
                                    style="BigFont.RoundedButtonDark.TButton", cursor="hand2", command=self._predict)
        predict_button.pack(expand=1, fill=tk.BOTH, padx=80, pady=(10, 30))

    def _go_through_tutorial(self, event):
        """
        This method open the sensor's placement tutorial

        :param event: the click Event
        """
        self.pack_forget()
        self.destroy()
        # Launching tutorial
        tutorial_page.TutorialPage(master=self._root, shimmers=self._shimmers,
                                   available_com_ports=self._available_com_ports,
                                   last_com_ports=self._last_com_ports).pack(expand=1, fill=tk.BOTH)

        # Helping Garbage Collector
        self._root = None
        self._selected_ports = None
        self._shimmers = None
        self._last_com_ports = None
        self._available_com_ports = None

    def _connect_all(self):
        """
        This method use TaskPopup to implements the connection with Shimmer devices.
        """
        # First of all checking if all COM ports are set
        for key, value in self._selected_ports.items():
            if key == util_shimmer.SHIMMER_IMU or key == util_shimmer.SHIMMER_BA or key == util_shimmer.SHIMMER_ExG_0 \
                    or key == util_shimmer.SHIMMER_ExG_1:
                continue
            else:
                if value.get() == "":
                    showerror("ERROR", "You have to choose COM port for all Shimmers")
                    return

        # If here, all COM ports are selected
        # Using TaskPopup to do the real connection
        popup = TaskPopup(master=self, func=self._func_connect_all,
                          args=(self._shimmers, self._selected_ports, self._last_com_ports),
                          caption="Setting up all Shimmers...")
        popup.start()
        self.wait_window(popup.top_level)

        # Preparing the connection info message
        message = ""
        all_ok = True
        for key, value in popup.result.items():
            if not value:
                all_ok = False
            message += key + " -> " + str(value) + "\n"
        if not all_ok:
            # Something went wrong with a connection. We want to disconnect all
            # Shimmer that were connected. (So no one is connected)
            showerror("ERROR", "Something went wrong during connection:\n" + message)
            popup = TaskPopup(master=self, func=self._func_disconnect_all, args=self._shimmers,
                              caption="Disconnecting all Shimmers")
            popup.start()
            self.wait_window(popup.top_level)
        else:
            # All connected, we have to change button from Connect to Disconnect All
            self._connect_button.pack_forget()
            self._disconnect_button.pack()

    def _disconnect_all(self):
        """
        This method use TaskPopup to implement the disconnection from the Shimmer3
        """
        # Check that all Shimmers are connected
        for shimmer in self._shimmers:
            # Here are supported only Shimmer3 GSR+, Shimmer3 ExG 0 and Shimmer3 ExG 1
            if shimmer.shimmer_type == util_shimmer.SHIMMER_IMU or shimmer.shimmer_type == util_shimmer.SHIMMER_BA:
                continue
            if shimmer.current_state != util_shimmer.BT_CONNECTED:
                # If the shimmer is not connected we don't have to do the disconnection
                return

        popup = TaskPopup(master=self, func=self._func_disconnect_all,
                          args=self._shimmers,
                          caption="Disconnecting all Shimmers...")
        popup.start()
        self.wait_window(popup.top_level)
        # Assuming there is no error
        self._disconnect_button.pack_forget()
        self._connect_button.pack()

    @staticmethod
    def _func_connect_all(shimmers, selected_ports, last_com_ports):
        """
        This function implements the connection with Shimmer3 devices.

        :param shimmers: Shimmer3 objects (those that we want to connect)
        :param selected_ports: selected ports for every Shimmer3
        :param last_com_ports: last COM ports used for last connection
        :return: a dict that tell for every Shimmer3 if the connection was successfully or not
        """
        results = {}
        for shimmer in shimmers:
            if not shimmer.current_state == util_shimmer.BT_CONNECTED:
                # It's supported only the Shimmer3 GSR+
                if shimmer.shimmer_type == util_shimmer.SHIMMER_IMU:
                    continue
                elif shimmer.shimmer_type == util_shimmer.SHIMMER_GSRplus:
                    results[shimmer.shimmer_type] = _func_connect_gsr(shimmer,
                                                                      selected_ports[shimmer.shimmer_type].get())
                elif shimmer.shimmer_type == util_shimmer.SHIMMER_ExG_0:
                    continue
                elif shimmer.shimmer_type == util_shimmer.SHIMMER_ExG_1:
                    continue
                elif shimmer.shimmer_type == util_shimmer.SHIMMER_BA:
                    continue

                if results[shimmer.shimmer_type]:
                    # If the connection goes right we want to update "last_com_ports"
                    last_com_ports[shimmer.shimmer_type] = selected_ports[shimmer.shimmer_type].get()
                    file = open('last_com_ports.pkl', 'wb')
                    pickle.dump(last_com_ports, file)
                    file.close()
        return results

    @staticmethod
    def _func_disconnect_all(*shimmers):
        """
        This function implements the disconnection from the Shimmers.

        :param shimmers: Shimmer3 objects (those that we want disconnect)
        """
        for shimmer in shimmers:
            if shimmer.current_state == util_shimmer.BT_CONNECTED:
                # Disconnect and reset properties to init
                shimmer.disconnect(reset_obj_to_init=True)

    def _predict(self):
        """
        This function start the prediction page. Is the callback linked to "Predict" button.
        """
        # The Shimmer3 GSR+ should be connected to use the predictor
        for shimmer in self._shimmers:
            if shimmer.shimmer_type == util_shimmer.SHIMMER_BA or shimmer.shimmer_type == util_shimmer.SHIMMER_IMU \
                    or shimmer.shimmer_type == util_shimmer.SHIMMER_ExG_0 or \
                    shimmer.shimmer_type == util_shimmer.SHIMMER_ExG_1:
                pass
            else:
                if shimmer.current_state != util_shimmer.BT_CONNECTED:
                    showerror("ERROR", "All the shimmer have to be connected")
                    return

        # Open up the prediction page
        page = prediction_page.PredictionPage(master=self, shimmers=self._shimmers, model=self._model)
        # Hiding this page
        self._root.withdraw()
        # Start the prediction loop
        page.start_prediction()

        self.wait_window(page.top_level)

        # Re-show the Main Menu page
        self._root.update()
        self._root.deiconify()
