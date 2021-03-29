import tkinter as tk
from tkinter import ttk

from gui import util
from gui.custom_mode import simultaneously_connections
from gui.wesad_mode import main_menu, tutorial_page
from gui import task_popup

import pickle

SELECTED_THEME = util.DRIBBBLE_THEME

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 200


class ModeSelectionPage(ttk.Frame):
    """
    This window allows the user to choose whether open the software in WESAD or Experimental mode.
    """
    def __init__(self, master=None, shimmers=None, available_com_ports=None, last_com_ports=None, model=None):
        super(ModeSelectionPage, self).__init__(master)

        # The 'master' here is the Tk root
        self._root = master
        self._root.resizable(False, False)
        # Settings window's size and position - Center the window
        position_from_left = int(self._root.winfo_screenwidth() / 2 - WINDOW_WIDTH / 2)
        position_from_top = int(self._root.winfo_screenheight() / 2 - WINDOW_HEIGHT / 2)
        self._root.geometry("{}x{}+{}+{}".format(WINDOW_WIDTH, WINDOW_HEIGHT, position_from_left, position_from_top))

        self._shimmers = shimmers
        self._available_com_ports = available_com_ports
        self._last_com_ports = last_com_ports
        self._model = model

        # Creating the left button -> WESAD mode
        self._wesad_btn_back = ttk.Frame(master=self, style="Button.Light.TFrame", cursor="hand2")
        self._wesad_btn_back.pack(expand=1, side=tk.LEFT, fill=tk.BOTH, ipadx=50, ipady=50)
        self._wesad_label = ttk.Label(master=self._wesad_btn_back, text="WESAD\nMODE", style="Big.Tab.TLabel")
        self._wesad_label.pack(expand=1)

        # Styling the button
        self._wesad_btn_back.bind("<Enter>", self.on_button_hover)
        self._wesad_btn_back.bind("<Leave>", self.on_button_leave)
        self._wesad_btn_back.bind("<Button-1>", self._start_wesad_mode)
        self._wesad_label.bind("<Button-1>", self._start_wesad_mode)

        # Creating the right button -> EXPERIMENTAL mode
        self._experimental_btn_back = ttk.Frame(master=self, style="Button.Light.TFrame", cursor="hand2")
        self._experimental_btn_back.pack(expand=1, side=tk.LEFT, fill=tk.BOTH, ipadx=50, ipady=50)
        self._experimental_label = ttk.Label(master=self._experimental_btn_back, text="EXPERIMENTAL\nMODE",
                                             style="Big.Tab.TLabel")
        self._experimental_label.pack(expand=1)

        # Styling the button
        self._experimental_btn_back.bind("<Enter>", self.on_button_hover)
        self._experimental_btn_back.bind("<Leave>", self.on_button_leave)
        self._experimental_btn_back.bind("<Button-1>", self._start_experimental_mode)
        self._experimental_label.bind("<Button-1>", self._start_experimental_mode)

    def _start_wesad_mode(self, event):
        # Check if we want to open the tutorial or if we should go directly to the main menu
        popup = task_popup.TaskPopup(master=self, func=self._check_first_run, args=(), caption="Wait...")
        popup.start()
        self.wait_window(popup.top_level)
        if popup.result:
            # First Run
            tutorial_page.TutorialPage(master=self._root, shimmers=self._shimmers,
                                       available_com_ports=self._available_com_ports,
                                       last_com_ports=self._last_com_ports, model=self._model).pack(expand=1, fill=tk.BOTH)
        else:
            # Not first run
            main_menu.MainMenu(master=self._root, shimmers=self._shimmers,
                               available_com_ports=self._available_com_ports,
                               last_com_ports=self._last_com_ports, model=self._model).pack(expand=1, fill=tk.BOTH)
        self.destroy()

    @staticmethod
    def _check_first_run():
        """
        This method check if this is the first time that the software is opened.
        :return: True if this is the first opening of the software, False otherwise
        """
        try:
            file = open("first_run.pkl", 'rb')
            file.close()
            return False
        except (FileNotFoundError, EOFError):
            # File not found -> first open, let's create the file for next openings
            file = open("first_run.pkl", 'wb')
            pickle.dump(False, file)
            file.close()
            return True

    def _start_experimental_mode(self, event):
        """
        This is the callback linked to the WESAD mode button

        :param event: the click Event
        """
        simultaneously_connections.SimultaneouslyConnections(master=self._root, sensors=self._shimmers,
                                                             available_ports=self._available_com_ports,
                                                             last_com_ports=self._last_com_ports).pack()
        self.destroy()

    def on_button_hover(self, event):
        """
        This method style buttons for mouse 'hover' event
        :param event: the hover Event (Enter)
        """
        event.widget["style"] = "ButtonDown.Dark.TFrame"
        if event.widget == self._wesad_btn_back:
            self._wesad_label["style"] = "DarkBack.Big.TLabel"
        else:
            self._experimental_label["style"] = "DarkBack.Big.TLabel"

    def on_button_leave(self, event):
        """
        This method style buttons for mouse 'leave' event
        :param event: the leave Event
        """
        event.widget["style"] = "Button.Light.TFrame"
        if event.widget == self._wesad_btn_back:
            self._wesad_label["style"] = "Big.Tab.TLabel"
        else:
            self._experimental_label["style"] = "Big.Tab.TLabel"
