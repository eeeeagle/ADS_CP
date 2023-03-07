from tkinter.ttk import Scale, LabelFrame
from tkinter import DoubleVar, IntVar, Frame, Button
from tktooltip import ToolTip
from entrywindow import change_value


class SoundSettingsFrame:
    _gain: DoubleVar
    _pan: IntVar
    _is_mute = False

    def __init__(self, master: Frame):
        self._gain = DoubleVar(master, value=0.0)
        self._pan = IntVar(master, value=0)

        # ROOT FRAME
        self._root = Frame(master, borderwidth=1, relief="solid")

        # BUTTONS
        self._mute_button = Button(self._root, text="Тихо", justify="center", anchor="n", command=self._mute)
        self._solo_button = Button(self._root, text="Соло", justify="center", anchor="n", command=self._solo)
        self._effects_button = Button(self._root, text="Эффекты", justify="center", anchor="n", command=self._effects)

        # GAIN FRAME
        gain_scale_frame = LabelFrame(self._root, text="Усиление", labelanchor="n")
        gain_scale = Scale(gain_scale_frame, orient="horizontal", length=100, from_=-36.0, to=36.0,
                           variable=self._gain, command=lambda e: self._gain.set(value=round(float(e), 0)))
        gain_scale.pack(side="top", fill="both", expand=True)

        gain_scale.bind("<Button-2>", func=lambda e: self._gain.set(value=0.0))
        gain_scale.bind("<Double-Button-1>", lambda e: change_value("Усиление", self._gain, -36.0, 36.0))
        ToolTip(gain_scale, msg=self._msg_gain)

        # PAN FRAME
        pan_scale_frame = LabelFrame(self._root, text="Баланс", labelanchor="n")
        pan_scale = Scale(pan_scale_frame, orient="horizontal", length=100, from_=-100, to=100,
                          variable=self._pan, command=lambda e: self._pan.set(value=round(float(e))))
        pan_scale.pack(side="top", fill="both", expand=True)
        pan_scale.bind("<Button-2>", func=lambda e: self._pan.set(value=0))
        pan_scale.bind("<Double-Button-1>", lambda e: change_value("Усиление", self._pan, -100, 100))
        ToolTip(pan_scale, msg=self._msg_pan)

        # SETTINGS GRID
        self._mute_button.grid(row=0, column=0, padx=2, pady=2, sticky="we")
        self._solo_button.grid(row=0, column=1, padx=2, pady=2, sticky="we")
        self._effects_button.grid(row=1, column=0, columnspan=2, padx=2, pady=2, sticky="we")
        gain_scale_frame.grid(row=2, column=0, columnspan=2, padx=2, pady=2, sticky="nsew")
        pan_scale_frame.grid(row=3, column=0, columnspan=2, padx=2, pady=2, sticky="nsew")

        self._root.grid_columnconfigure(0, weight=1)
        self._root.grid_columnconfigure(1, weight=1)

    def _msg_gain(self):
        return "Усиление: " + str(self._gain.get()) + " дБ"

    def _msg_pan(self):
        if self._pan.get() > 0.0:
            return "Баланс: " + str(round(self._pan.get())) + "% правый"
        if self._pan.get() < 0.0:
            return "Баланс: " + str(abs(round(self._pan.get()))) + "% левый"
        return "Баланс: центр"

    def _effects(self):
        print("effects")

    def _solo(self):
        if not self._is_mute:
            self._is_mute = True

    def _mute(self):
        if self._is_mute:
            self._is_mute = False
            self._mute_button.configure(relief="raised")
        else:
            self._is_mute = True
            self._mute_button.configure(relief="sunken")

    def get_gain(self):
        return self._gain.get()

    def get_pan(self):
        return self._pan.get() / 100

    def is_muted(self):
        return self._is_mute

    def grid(self, row: int, column: int, sticky: str):
        self._root.grid(row=row, column=column, sticky=sticky)

    def grid_show(self):
        self._root.grid()

    def grid_remove(self):
        self._root.grid_remove()
