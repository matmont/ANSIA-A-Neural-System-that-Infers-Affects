import tkinter as tk
from tkinter import StringVar
from tkinter import ttk

from gui import util as util_gui
from gui.wesad_mode import main_menu
from shimmer import util as util_shimmer

SELECTED_THEME = util_gui.DRIBBBLE_THEME


# General Tutorial Tab
class TutorialTab(ttk.Frame):
    """
    This is a general tutorial tab. We will specialize this class to implement tutorial for every Shimmer3 device.
    """
    def __init__(self, master=None):
        super(TutorialTab, self).__init__(master=master, style="Light.TFrame")

        """
        Layout Idea:
            
            +--------------------------------+
            |                                |
            |                                |
            +                                +
            |                                |
            |  written            maybe      |
            |  hints              the image  |
            |                                |
            |                                |
            +--------------------------------+
            
        """

        # Configuring grid entities
        self.rowconfigure((0, 1), weight=1)
        self.columnconfigure((0, 1), weight=1)

        # Upper frame section -> COM Port
        upper_frame = ttk.Frame(self, style="Light.TFrame")
        upper_frame.grid(row=0, column=0, columnspan=2, pady=20)

        # Left frame section -> Written hints
        written_hints_frame = ttk.Frame(self, style="Light.TFrame")
        written_hints_frame.grid(row=1, column=0)

        written_hints_text = ttk.Label(written_hints_frame, text=self._written_hints_message())
        written_hints_text.pack(expand=1)

        # Right frame section -> Images
        image_frame = ttk.Frame(self, style="Light.TFrame")
        image_frame.grid(row=1, column=1)

        # we have to insert the image
        image_canvas = tk.Canvas(image_frame, width=350, height=self._get_image_height(),
                                 background=SELECTED_THEME["light_frame_background"])
        self._image_img = tk.PhotoImage(data=self._get_image())
        image_canvas.create_image(0, 0, anchor="nw", image=self._image_img)
        image_canvas.pack(expand=1, fill=tk.BOTH)

    @staticmethod
    def _written_hints_message():
        return "This is the general written hint.\nYou should override this method..."

    @staticmethod
    def _get_image():
        return None

    @staticmethod
    def _get_image_height():
        return 350

    def _connect(self):
        pass


class GSR_TutorialTab(TutorialTab):
    """
    This is the tutorial tab for the Shimmer3 GSR+.
    """
    def __init__(self, master=None):
        super(GSR_TutorialTab, self).__init__(master=master)

    @staticmethod
    def _written_hints_message():
        return "1. Take the Shimmer GSR+.\n" \
               "2. Check 'discover how' link to see\nhow to get the COM Port.\n" \
               "3. Place it on your wrist with the strap.\n" \
               "4. Check the image on the right to see the sensors placement.\n"

    @staticmethod
    def _get_image():
        return SELECTED_THEME["gsrplus_photo"]


class EMG_TutorialTab(TutorialTab):
    """
    This is the tutorial tab for the Shimmer3 ExG for EMG.
    """
    def __init__(self, master=None):
        super(EMG_TutorialTab, self).__init__(master=master)

    @staticmethod
    def _written_hints_message():
        return "1. Take the Shimmer ExG. \n" \
               "2. Check 'discover how' link to see\nhow to get the COM Port.\n" \
               "3. Place it on your chest with the strap.\n" \
               "4. Check the image on the right to see the electrodes placement.\nThe EMG data is " \
               "recorded on the upper trapezius\n muscle on both sides of the spine. \nThe REFERENCE electrode " \
               "should be\n" \
               "placed on a bone region (red circle in the image)."

    @staticmethod
    def _get_image():
        return SELECTED_THEME["emg_photo"]


class RESP_TutorialTab(TutorialTab):
    """
    This is the tutorial tab for the Shimmer3 ExG for Respiration
    """
    def __init__(self, master=None):
        super(RESP_TutorialTab, self).__init__(master=master)

    @staticmethod
    def _written_hints_message():
        return "1. Take the Shimmer ExG. \n" \
               "2. Check 'discover how' link to see\nhow to get the COM Port.\n" \
               "3. Place it on your chest with the strap.\n" \
               "4. Check the image on the right to see the electrodes placement.\n" \
               "Note that LL (red) and V1 (brown) electrodes are optional.\n" \
               "Place RA (white) on the right mid-axillary line and the LA (black)\n" \
               "on the left mid-axillary line (into the V6 position of ECG electrodes).\n" \
               "The RL (green) electrode is the REFERENCE."

    @staticmethod
    def _get_image():
        return SELECTED_THEME["resp_photo"]

    @staticmethod
    def _get_image_height():
        return 500


WINDOW_HEIGHT = 700
WINDOW_WIDTH = 900

DEBUG = True


class TutorialPage(ttk.Frame):
    def __init__(self, master=None, shimmers=None, available_com_ports=None, last_com_ports=None, model=None):
        super(TutorialPage, self).__init__(master=master, style="Light.TFrame")

        # Master should be the Tk root
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

        # It will be used as a 'textvariable' for the Shimmer label - see below
        self._current_shimmer_tutorial = StringVar(value=util_shimmer.SHIMMER_GSRplus)

        # Setting the row/column settings
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Main Title
        shimmer_title = ttk.Label(master=self, textvariable=self._current_shimmer_tutorial, style="Big.TLabel")
        shimmer_title.grid(row=0, column=0)

        # GSR+ tutorial page
        self._gsr_tutorial_page = GSR_TutorialTab(master=self)
        self._gsr_tutorial_page.grid(row=1, column=0, sticky="nwes")

        # ExG 0 (EMG) tutorial page
        self._emg_tutorial_page = EMG_TutorialTab(master=self)

        # ExG 1 (RESP) tutorial page
        self._resp_tutorial_page = RESP_TutorialTab(master=self)

        # "Next" section
        next_frame = ttk.Frame(self, style="Light.TFrame")
        next_frame.grid(row=2, column=0, pady=20)
        next_btn = ttk.Button(master=next_frame, text="Next",
                              style="RoundedButtonLight.TButton", command=self._connect_and_next, cursor="hand2")
        next_btn.pack(side=tk.LEFT, padx=5)

    def _connect_and_next(self):
        # This is the current shimmer's type
        current_shimmer = self._current_shimmer_tutorial.get()

        if current_shimmer == util_shimmer.SHIMMER_GSRplus:
            self._current_shimmer_tutorial.set("EMG")
            self._gsr_tutorial_page.grid_forget()
            self._gsr_tutorial_page.destroy()
            self._gsr_tutorial_page = None
            self._emg_tutorial_page.grid(row=1, column=0, sticky="nwes")
        elif current_shimmer == "EMG":
            self._current_shimmer_tutorial.set("RESP")
            self._emg_tutorial_page.grid_forget()
            self._emg_tutorial_page.destroy()
            self._emg_tutorial_page = None
            self._resp_tutorial_page.grid(row=1, column=0, sticky="nwes")
        elif current_shimmer == "RESP":
            self._resp_tutorial_page.grid_forget()
            self._resp_tutorial_page.destroy()
            self._resp_tutorial_page = None
            # Now we should go to the main menu
            self.pack_forget()
            self.destroy()
            main_menu.MainMenu(master=self._root, shimmers=self._shimmers,
                               available_com_ports=self._available_com_ports, last_com_ports=self._last_com_ports, model=self._model).pack(
                expand=1, fill=tk.BOTH)
