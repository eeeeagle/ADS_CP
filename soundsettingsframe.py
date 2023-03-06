import threading

from tkinter.ttk import Scale
from tkinter import DoubleVar, IntVar, Frame, Button
from tktooltip import ToolTip
from entrywindow import EntryWindow


class SoundSettingsFrame:
    _gain: DoubleVar
    _pan: IntVar
    _is_mute = False

    def __init__(self, master: Frame):
        self._gain = DoubleVar(master, value=0.0)
        self._pan = IntVar(master, value=0)

        # ROOT FRAME
        self.root = Frame(master, borderwidth=1, relief="solid")

        # BUTTONS
        self._mute_sound_button = Button(self.root, text="Тихо", justify="center", anchor="n", command=self._mute)
        self._solo_sound_button = Button(self.root, text="Соло", justify="center", anchor="n", command=self._solo)

        # GAIN SCALE
        self._gain_scale = Scale(self.root, orient="horizontal", length=120, from_=-36.0, to=36.0,
                                 variable=self._gain, command=lambda s: self._gain.set(value=round(float(s), 0)))
        self._gain_scale.bind("<Button-2>", func=lambda e: self._gain.set(value=0.0))
        self._gain_scale.bind("<Double-Button-1>", lambda e: self._change_gain)
        ToolTip(self._gain_scale, msg=self._msg_gain)

        # PAN SCALE
        self._pan_scale = Scale(self.root, orient="horizontal", length=120, from_=-100, to=100,
                                variable=self._pan, command=lambda s: self._pan.set(value=round(float(s))))
        self._pan_scale.bind("<Button-2>", func=lambda e: self._pan.set(value=0))
        self._pan_scale.bind("<Double-Button-1>", lambda e: self._change_pan)
        ToolTip(self._pan_scale, msg=self._msg_pan)

        # SETTINGS GRID
        self._mute_sound_button.grid(row=0, column=0, padx=2, pady=2, sticky="we")
        self._solo_sound_button.grid(row=0, column=1, padx=2, pady=2, sticky="we")
        self._gain_scale.grid(row=1, column=0, columnspan=2, padx=2, pady=2, sticky="we")
        self._pan_scale.grid(row=2, column=0, columnspan=2, padx=2, pady=2, sticky="we")

    def _change_gain(self):
        def extra_window():
            window = EntryWindow("Усиление", self._gain.get(), -36.0, 36.0)
            self._gain.set(value=window.value)

        thr = threading.Thread(target=extra_window, args=())
        thr.start()

    def _change_pan(self):
        def extra_window():
            window = EntryWindow("Баланс", self._pan.get(), -100, 100)
            self._pan.set(value=window.value)

        thr = threading.Thread(target=extra_window, args=())
        thr.start()

    def _msg_gain(self):
        return "Усиление: " + str(self._gain.get()) + " дБ"

    def _msg_pan(self):
        if self._pan.get() > 0.0:
            return "Баланс: " + str(round(self._pan.get())) + "% правый"
        if self._pan.get() < 0.0:
            return "Баланс: " + str(abs(round(self._pan.get()))) + "% левый"
        return "Баланс: центр"

    def _solo(self):
        if not self._is_mute:
            self._is_mute = True

    def _mute(self):
        if self._is_mute:
            self._is_mute = False
            self._mute_sound_button.configure(relief="raised")
        else:
            self._is_mute = True
            self._mute_sound_button.configure(relief="sunken")

    def hide(self):
        self.root.pack_forget()

    def get_gain(self):
        return self._gain.get()

    def get_pan(self):
        return self._pan.get() / 100

    def is_muted(self):
        return self._is_mute
