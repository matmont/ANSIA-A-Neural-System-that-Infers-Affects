import pickle
import sys
from tkinter import font

import numpy as np
import tensorflow as tf
from serial.tools import list_ports

from gui import util as util_gui
from gui.custom_mode.mainpage import *
from gui.mode_selection_page import ModeSelectionPage
from models import simple_deep_esn_classifier
from shimmer import util as util_shimmer
from shimmer.shimmer import Shimmer3

root = tk.Tk()
root.title("ANSIA")
root.minsize(width=300, height=200)

# Settings theme (not the real ttkinter theme)
SELECTED_THEME = util_gui.DRIBBBLE_THEME

# Fonts
family = SELECTED_THEME["font_family"]
size = SELECTED_THEME["font_size"]
bold_font = font.Font(family=family, size=size, weight=font.BOLD)
normal_font = font.Font(family=family, size=size, weight=font.NORMAL)
smaller_font = font.Font(family=family, size=int(size * 3 / 4), weight=font.NORMAL)
link_font = font.Font(family=family, size=int(size * 3 / 4), weight=font.NORMAL, underline=1)
big_font = font.Font(family=family, size=int(size * 1.5), weight=font.BOLD)

style = ttk.Style()

# Creating THEME
style.theme_create("AnsiaTheme", parent="alt", settings={
    ".": {
        "configure": {
            "font": bold_font
        }
    },
    "TButton": {
        "configure": {
            "padding": (20, 8),
            "background": SELECTED_THEME["btn_bg_normal_color"],
            "anchor": tk.CENTER,
            "focuscolor": SELECTED_THEME["dark_frame_background"],
            "borderwidth": 1,
            "relief": tk.SOLID,
            "foreground": SELECTED_THEME["btn_text_normal_color"],
            "font": bold_font,
        },
        "map": {
            "relief": [("active", tk.SOLID)],
            "background": [("active", SELECTED_THEME["btn_bg_over_color"]),
                           ("disabled", SELECTED_THEME["disabled_frame_background"])],
            "focuscolor": [("active", SELECTED_THEME["dark_frame_background"])],
            "foreground": [("active", SELECTED_THEME["btn_text_over_color"])],
            "borderwidth": [("active", 1)]
        }
    },
    "TNotebook": {
        "configure": {
            "background": SELECTED_THEME["dark_frame_background"],
            "padding": 15,
            "relief": tk.FLAT,
            "borderwidth": 0,
            "highlightthickness": 0,
        }
    },
    "TNotebook.Tab": {
        "configure": {
            "background": SELECTED_THEME["normal_tab_color"],
            "focuscolor": SELECTED_THEME["selected_tab_color"],  # la linea tratteggiata intorno..
            "relief": tk.FLAT,
            "borderwidth": 0,
            "padding": (20, 20),
            "foreground": SELECTED_THEME["normal_tab_text_color"],
            "font": bold_font,
            "highlightthickness": 0
        },
        "map": {
            "background": [("selected", SELECTED_THEME["selected_tab_color"]),
                           ("active", SELECTED_THEME["mouseover_tab_color"])],
            "foreground": [("selected", SELECTED_THEME["selected_tab_text_color"]),
                           ("active", SELECTED_THEME["mouseover_tab_text_color"])]

        }
    },
    "TFrame": {
        "configure": {
            "background": SELECTED_THEME["dark_frame_background"],
            "borderwidth": 0,
            "highlightthickness": 0,
            "relief": tk.FLAT
        }
    },
    "TLabel": {
        "configure": {
            "background": SELECTED_THEME["light_frame_background"],
            "foreground": "white",
            "anchor": tk.CENTER,
            "justify": tk.CENTER
        }
    },
    "TEntry": {
        "configure": {
            "padding": 8,
            "relief": tk.FLAT,
            "highlightthickness": 0,
            "borderwidth": 0,
        }
    },
    "TCombobox": {
        "configure": {
            "padding": 5,
            "selectbackground": "white",
            "selectforeground": "black",
            "borderwidth": 0,
            "arrowsize": 1,
            "highlightthickness": 0,
            "relief": tk.FLAT
        }
    },
    "TCheckbutton": {
        "configure": {
            "borderwidth": 0,
            "padding": 5,
            "background": SELECTED_THEME["light_frame_background"],
            "indicatorrelief": tk.FLAT,
            "indicatormargin": 5,
            "indicatordiameter": 10,
        }
    }
})
style.theme_use("AnsiaTheme")
style.configure("Dark.TFrame", background=SELECTED_THEME["dark_frame_background"])
style.configure("Red.TNotebook", background="red")
style.configure("Light.TFrame", background=SELECTED_THEME["light_frame_background"])
style.configure("Tab.TFrame", background=SELECTED_THEME["selected_tab_color"])
style.configure("Red.TFrame", background="red")  # for Debug purposes
style.configure("Green.TFrame", background="green")  # for Debug purposes
style.configure("Yellow.TFrame", background="yellow")  # for Debug purposes
style.configure("Bordered.TFrame", borderwidth=1, relief=tk.RAISED)
style.configure("Disabled.TFrame", background=SELECTED_THEME["disabled_frame_background"])
style.configure("Warning.TLabel", foreground=SELECTED_THEME["contrast_color"], font=smaller_font)
style.configure("DarkBack.Warning.TLabel", background=SELECTED_THEME["dark_frame_background"])
style.configure("DarkBack.TLabel", background=SELECTED_THEME["dark_frame_background"])
style.configure("Small.TLabel", font=smaller_font)
style.configure("Light.TLabel", font=normal_font)
style.configure("Link.Small.TLabel", foreground=SELECTED_THEME["link_normal_text_color"], font=link_font)
style.configure("DarkBack.Link.Small.TLabel", background=SELECTED_THEME["dark_frame_background"])
style.configure("DarkBack.Big.TLabel", background=SELECTED_THEME["dark_frame_background"])
style.configure("Big.TLabel", font=big_font)
style.configure("Big.Tab.TLabel", font=big_font, background=SELECTED_THEME["selected_tab_color"])
style.configure("DarkBack.Big.TLabel", font=big_font, background=SELECTED_THEME["dark_frame_background"])
style.configure("Button.Light.TFrame", relief=tk.RAISED, borderwidth=10)
style.configure("ButtonDown.Dark.TFrame", relief=tk.RAISED, borderwidth=4)
# Rounded Button when Back is dark

image_rounded_btn_normal_darkback = tk.PhotoImage("image_rounded_btn_normal_darkback",
                                                  data=SELECTED_THEME["dark_rounded_bg_darkback"])
image_rounded_btn_active_darkback = tk.PhotoImage("image_rounded_btn_active_darkback",
                                                  data=SELECTED_THEME["light_rounded_bg_darkback"])
image_rounded_btn_pressed_darkback = tk.PhotoImage("image_rounded_btn_pressed_darkback",
                                                   data=SELECTED_THEME["light2_rounded_bg_darkback"])

style.element_create("RoundedButtonDark", "image", image_rounded_btn_normal_darkback,
                     ("pressed", image_rounded_btn_pressed_darkback), ("active", image_rounded_btn_active_darkback),
                     border=16, sticky="nsew")
style.layout("RoundedButtonDark.TButton",
             [("RoundedButtonDark", {"sticky": "nsew"}),
              ("Menubutton.button", {"children": [("Menubutton.focus",
                                                   {"children": [
                                                       ("Menubutton.padding", {"children": [("Menubutton.label",
                                                                                             {"side": "left",
                                                                                              "expand": 1})]})]})]})])
style.configure("RoundedButtonDark.TButton",
                focuscolor=SELECTED_THEME["dark_frame_background"],
                foreground="white")
style.configure("BigLabel.RoundedButtonDark.TButton",
                focuscolor=SELECTED_THEME["dark_frame_background"],
                foreground="white",
                font=big_font)

# Rounded Button when Back is dark

image_rounded_btn_normal_lightback = tk.PhotoImage("image_rounded_btn_normal_lightback",
                                                   data=SELECTED_THEME["dark_rounded_bg_lightback"])
image_rounded_btn_active_lightback = tk.PhotoImage("image_rounded_btn_active_lightback",
                                                   data=SELECTED_THEME["light_rounded_bg_lightback"])
image_rounded_btn_pressed_lightback = tk.PhotoImage("image_rounded_btn_pressed_lightback",
                                                    data=SELECTED_THEME["light2_rounded_bg_lightback"])

style.element_create("RoundedButtonLight", "image", image_rounded_btn_normal_lightback,
                     ("pressed", image_rounded_btn_pressed_lightback), ("active", image_rounded_btn_active_lightback),
                     border=16,
                     sticky="nsew")
style.layout("RoundedButtonLight.TButton",
             [("RoundedButtonLight", {"sticky": "nsew"}),
              ("Menubutton.button", {"children": [
                  ("Menubutton.padding", {"children": [("Menubutton.label",
                                                        {"side": "left",
                                                         "expand": 1})]})]})])
style.configure("RoundedButtonLight.TButton",
                focuscolor=SELECTED_THEME["light_frame_background"],
                foreground="white")

style.configure("BigFont.RoundedButtonLight.TButton",
                font=big_font)
# Combobox with custom arrow

image_downarrow = tk.PhotoImage("image_downarrow", data=SELECTED_THEME["downarrow"])

style.element_create("CustomCombobox.TCombobox.downarrow", "image", image_downarrow)

style.layout('CustomCombobox.TCombobox', [(
    'Combobox.field', {
        'sticky': "nsew",
        'children': [(
            'CustomCombobox.TCombobox.downarrow', {
                'side': 'right',
                'sticky': "ns"
            }
        ), (
            'Combobox.padding', {
                'expand': '1',
                'sticky': "nsew",
                'children': [(
                    'Combobox.textarea', {
                        'sticky': "nsew"
                    }
                )]
            }
        )]
    }
)])

# Rounded Frame

image_frame_back = tk.PhotoImage("image_frame_back", data=SELECTED_THEME["light_rounded_tabframe_bg_darkback"])
style.element_create("RoundedFrameBack", "image", image_frame_back, border=10, sticky="nwes")
style.layout("RoundedFrame.Tab.TFrame", [
    ("RoundedFrameBack", {"sticky": "nsew"}),
    ("Frame.border", {"sticky": "nsew"})
])

########################################################################

# All available sensors
sensors = [
    Shimmer3(shimmer_type=util_shimmer.SHIMMER_IMU, debug=True),
    Shimmer3(shimmer_type=util_shimmer.SHIMMER_GSRplus, debug=True),
    Shimmer3(shimmer_type=util_shimmer.SHIMMER_ExG_0, debug=True),
    Shimmer3(shimmer_type=util_shimmer.SHIMMER_ExG_1, debug=True),
    Shimmer3(shimmer_type=util_shimmer.SHIMMER_BA, debug=True)
]


def func_setup():
    """
    This function is executed at the program's start. It retrieves a list of the
    available COM ports on the host and the last used ports for each sensors (if there are).

    *If available ports are empty, we can assume that the Bluetooth is not enabled in the host: the user
    will be notified to turn on it.*

    :return: all available COM ports in the first position, last used ports in the second
    :rtype: list
    """
    # Retrieving model
    NUM_CLASSES = 2
    UNITS = 500
    LAYERS = 5
    SEQ_TO_SEQ = True
    CONCAT = True
    if LAYERS == 1:
        CONCAT = False
    LEAKY = 1
    SPECTRAL_RADIUS = 0.5
    INPUT_SCALING = 0.5

    params = np.load('models/model1.npy', allow_pickle=True)
    params = params[()]

    np.random.seed(0)
    tf.random.set_seed(0)
    model = simple_deep_esn_classifier.SimpleDeepESNClassifier(num_classes=NUM_CLASSES, units=UNITS, layers=LAYERS,
                                                               return_sequences=SEQ_TO_SEQ, concat=CONCAT, leaky=LEAKY,
                                                               spectral_radius=SPECTRAL_RADIUS,
                                                               input_scaling=INPUT_SCALING)
    model.build(input_shape=(1, None, 3))
    model.set_w(params)

    # Listing all the available ports
    ports = []
    for port in list_ports.comports():
        ports.append(port.device)

    # Checking if exists 'last_com_ports' file
    try:
        file = open('last_com_ports.pkl', 'rb')
        last_com_ports = pickle.load(file)
        file.close()
    except (FileNotFoundError, EOFError):
        # If not, we create a init dict for this
        last_com_ports = {
            util_shimmer.SHIMMER_IMU: None,
            util_shimmer.SHIMMER_GSRplus: None,
            util_shimmer.SHIMMER_ExG_0: None,
            util_shimmer.SHIMMER_ExG_1: None,
            util_shimmer.SHIMMER_BA: None
        }

    return [ports, last_com_ports, model]


# Starting the popup that show to user the loading sign: in background it will be executed the previous function
popup = TaskPopup(master=root, func=func_setup, args=(), caption="Initializing software...")
popup.start()

# Hide the root window while AsyncTaskPopup is working
root.withdraw()
# Block the code execution until AsyncTaskPopup hasn't finished
root.wait_window(popup.top_level)

# Retrieve task result
result = popup.result
if not result[0]:
    # 'if not list' is True when 'list' is empty: if result[0] (available COM ports on host) is empty,
    # then (probably) the Bluetooth is turned off.
    showerror("ERROR", "Be sure that you have turned on the Bluetooth on your pc.\n\nThe software will be closed.")
else:
    # Creating various page's objects - note that sensors == shimmers for now
    mode_selection_page = ModeSelectionPage(master=root, shimmers=sensors,
                                            available_com_ports=result[0], last_com_ports=result[1], model=result[2])
    # Re-show the root window
    root.update()
    root.deiconify()
    # "Deleting" popup -> this will help the Garbage Collector
    popup = None

    # The first window is the ModeSelectionPage
    mode_selection_page.pack(expand=1, fill=tk.BOTH)

    sys.exit(root.mainloop())
