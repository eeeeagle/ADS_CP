import threading

from tkinter.ttk import Scale, LabelFrame
from tkinter import DoubleVar, IntVar, Frame, Button
from tktooltip import ToolTip
from entrywindow import EntryWindow


class SoundSettingsFrame:
    def __init__(self, master: LabelFrame):
        # VARIABLES
        self.master = master
        self.gain = DoubleVar(value=0.0)
        self.pan = IntVar(value=0)
        self.is_hide = False
        self.is_mute = False

        # ROOT FRAME
        self.settings_frame = Frame(self.master, borderwidth=1, relief="ridge")
        self.settings_frame.pack(side="left", expand=True, fill="y")

        # BUTTONS
        self.delete_sound_button = Button(self.settings_frame, text="Закрыть", justify="center", command=self._destroy)
        self.hide_sound_button = Button(self.settings_frame, text="Скрыть", justify="center", command=self._hide)
        self.mute_sound_button = Button(self.settings_frame, text="Тихо", justify="center", command=self._mute)
        self.solo_sound_button = Button(self.settings_frame, text="Соло", justify="center", command=self._solo)

        # GAIN SCALE
        self.gain_scale = Scale(self.settings_frame, orient="horizontal", length=100, from_=-36.0, to=36.0,
                                variable=self.gain, command=lambda s: self.gain.set(value=round(float(s), 0)))
        self.gain_scale.bind("<Button-2>", func=lambda e: self.gain.set(value=0.0))
        self.gain_scale.bind("<Double-Button-1>", lambda s: self._change_gain)
        ToolTip(self.gain_scale, msg=self._msg_gain, delay=0)

        # PAN SCALE
        self.pan_scale = Scale(self.settings_frame, orient="horizontal", length=100, from_=-100, to=100,
                               variable=self.pan, command=lambda s: self.pan.set(value=round(float(s))))
        self.pan_scale.bind("<Button-2>", func=lambda e: self.pan.set(value=0))
        self.pan_scale.bind("<Double-Button-1>", lambda s: self._change_pan)
        ToolTip(self.pan_scale, msg=self._msg_pan, delay=0)

        # SETTINGS GRID
        self.delete_sound_button.grid(row=0, column=0, sticky="we", padx=2, pady=2)
        self.hide_sound_button.grid(row=0, column=1, sticky="we", padx=2, pady=2)
        self.mute_sound_button.grid(row=1, column=0, sticky="we", padx=2, pady=2)
        self.solo_sound_button.grid(row=1, column=1, sticky="we", padx=2, pady=2)
        self.gain_scale.grid(row=2, column=0, columnspan=2, padx=2, pady=2)
        self.pan_scale.grid(row=3, column=0, columnspan=2, padx=2, pady=2)

    def _change_gain(self):
        def extra_window():
            window = EntryWindow("Усиление", self.gain.get(), -36.0, 36.0)
            self.gain.set(value=window.value)

        thr = threading.Thread(target=extra_window, args=())
        thr.start()

    def _change_pan(self):
        def extra_window():
            window = EntryWindow("Баланс", self.pan.get(), -100, 100)
            self.pan.set(value=window.value)

        thr = threading.Thread(target=extra_window, args=())
        thr.start()

    def _msg_gain(self):
        return "Усиление: " + str(self.gain.get()) + " дБ"

    def _msg_pan(self):
        if self.pan.get() > 0.0:
            return "Баланс: " + str(round(self.pan.get())) + "% правый"
        if self.pan.get() < 0.0:
            return "Баланс: " + str(abs(round(self.pan.get()))) + "% левый"
        return "Баланс: центр"

    def _destroy(self):
        self.master.destroy()

    def _hide(self):
        if self.is_hide:
            self.is_hide = False
            self.master.pack_forget()
        else:
            self.master.pack()
            self.is_hide = True

    def _mute(self):
        if self.is_mute:
            self.is_mute = False
            self.mute_sound_button.configure(relief="raised")
        else:
            self.is_mute = True
            self.mute_sound_button.configure(relief="sunken")

    def _solo(self):
        if not self.is_mute:
            self.is_mute = True

    def is_muted(self):
        return self.is_mute

    def is_hide(self):
        return self.is_hide

    def get_gain(self):
        return self.gain.get()

    def get_pan(self):
        return self.pan.get() / 100
