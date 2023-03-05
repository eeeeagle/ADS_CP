from tkinter.ttk import Label, Scale, LabelFrame
from tkinter import DoubleVar, Frame, Button
from tktooltip import ToolTip


class SoundSettingsFrame:
    def __init__(self, master: LabelFrame):
        # VARIABLES
        self.master = master
        self.gain = DoubleVar(value=0.0)
        self.pan = DoubleVar(value=0.0)
        self.is_hide = False
        self.is_mute = False

        # SETTINGS FRAME
        self.settings_frame = Frame(self.master, borderwidth=1, relief="ridge")
        self.settings_frame.pack(side="left")

        # SETTINGS BUTTONS
        self.delete_sound_button = Button(self.settings_frame, text="Закрыть", justify="center", command=self._destroy)
        self.hide_sound_button = Button(self.settings_frame, text="Скрыть", justify="center", command=self._hide)
        self.mute_sound_button = Button(self.settings_frame, text="Тихо", justify="center", command=self._mute)
        self.solo_sound_button = Button(self.settings_frame, text="Соло", justify="center", command=self._solo)

        # SETTINGS VOLUME SCALE
        self.gain_scale = Scale(self.settings_frame, orient="horizontal", length=100, from_=-30.0, to=30.0,
                                variable=self.gain, command=lambda s: self.gain.set(value=round(float(s), 0)))

        # SETTINGS PAN SCALE
        self.pan_scale = Scale(self.settings_frame, orient="horizontal", length=100, from_=-1.0, to=1.0,
                               variable=self.pan, command=lambda s: self.pan.set(value=round(float(s), 1)))

        ToolTip(self.gain_scale, msg=self._msg_gain, delay=0)
        ToolTip(self.pan_scale, msg=self._msg_pan, delay=0)

        # SETTINGS GRID
        self.delete_sound_button.grid(row=0, column=0, sticky="we", padx=2, pady=2)
        self.hide_sound_button.grid(row=0, column=1, sticky="we", padx=2, pady=2)
        self.mute_sound_button.grid(row=1, column=0, sticky="we", padx=2, pady=2)
        self.solo_sound_button.grid(row=1, column=1, sticky="we", padx=2, pady=2)
        self.gain_scale.grid(row=2, column=0, columnspan=2, padx=2, pady=2)
        self.pan_scale.grid(row=3, column=0, columnspan=2, padx=2, pady=2)

    def _msg_gain(self):
        return "Усиление: " + str(self.gain.get()) + " дБ"

    def _msg_pan(self):
        if self.pan.get() > 0.0:
            return "Баланс: " + str(round(self.pan.get() * 100)) + "% правый"
        if self.pan.get() < 0.0:
            return "Баланс: " + str(abs(round(self.pan.get() * 100))) + "% левый"
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
        return self.pan.get()
