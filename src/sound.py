import numpy as np

from sample_waveform import SampleWaveform
from tktooltip import ToolTip
from value_window import change_value
from pydub import AudioSegment
from tkinter.ttk import Frame, Scale, LabelFrame
from tkinter import Button, Label, Frame, DoubleVar, IntVar
from effects_window import apply_effect


class Sound:
    solo_id = -1
    delete_allowed = True
    _id = 0

    def __init__(self, master: Frame, filename: str):
        # VARIABLES
        self._sound = AudioSegment.from_file(filename, filename.split('.')[-1])
        self._sample_width = self._sound.sample_width
        self._frame_rate = self._sound.frame_rate
        self._channels = self._sound.channels

        self._gain = DoubleVar(value=0.0)
        self._pan = IntVar(value=0)

        self._is_close = False
        self._is_hide = False
        self._is_mute = False

        self._waveform_list = list[SampleWaveform]()

        self.ID = Sound._id
        Sound._id += 1

        # ROOT
        self._root = Frame(master)
        settings_frame = Frame(self._root, borderwidth=1, relief="solid")
        waveform_frame = Frame(self._root, borderwidth=1, relief="solid")

        # BUTTONS
        close_button = Button(settings_frame, text="Закрыть", justify="center", command=self._close)
        self._hide_button = Button(settings_frame, text="Скрыть", justify="center", command=self._hide)
        self._mute_button = Button(settings_frame, text="Тихо", justify="center", command=self._mute)
        self._solo_button = Button(settings_frame, text="Соло", justify="center", command=self._solo)
        self._effects_button = Button(settings_frame, text="Эффекты", justify="center", command=self._effects)

        # GAIN FRAME
        self._gain_scale_frame = LabelFrame(settings_frame, text="Усиление", labelanchor="n")
        self._gain_scale = Scale(self._gain_scale_frame, orient="horizontal", length=100, from_=-36.0, to=36.0,
                                 variable=self._gain, command=lambda e: self._gain.set(value=round(float(e), 0)))
        self._gain_scale.pack(side="top", fill="both", expand=True)

        self._gain_scale.bind("<Button-2>", func=lambda e: self._gain.set(value=0.0))
        self._gain_scale.bind("<Double-Button-1>", lambda e: change_value("Усиление", self._gain, -36.0, 36.0))
        ToolTip(self._gain_scale, msg=self._msg_gain)

        # PAN FRAME
        self._pan_scale_frame = LabelFrame(settings_frame, text="Баланс", labelanchor="n")
        self._pan_scale = Scale(self._pan_scale_frame, orient="horizontal", length=100, from_=-100, to=100,
                                variable=self._pan, command=lambda e: self._pan.set(value=round(float(e))))
        self._pan_scale.pack(side="top", fill="both", expand=True)
        self._pan_scale.bind("<Button-2>", func=lambda e: self._pan.set(value=0))
        self._pan_scale.bind("<Double-Button-1>", lambda e: change_value("Усиление", self._pan, -100, 100))
        ToolTip(self._pan_scale, msg=self._msg_pan)

        # LABELS
        #
        # TO DO
        #

        # SETTINGS GRID
        close_button.grid(row=0, column=0, padx=2, pady=2, sticky="we")
        self._hide_button.grid(row=0, column=1, padx=2, pady=2, sticky="we")
        self._mute_button.grid(row=1, column=0, padx=2, pady=2, sticky="we")
        self._solo_button.grid(row=1, column=1, padx=2, pady=2, sticky="we")
        self._effects_button.grid(row=2, column=0, columnspan=2, padx=2, pady=2, sticky="we")
        self._gain_scale_frame.grid(row=3, column=0, columnspan=2, padx=2, pady=2, sticky="nsew")
        self._pan_scale_frame.grid(row=4, column=0, columnspan=2, padx=2, pady=2, sticky="nsew")

        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(1, weight=1)

        # WAVEFORM FRAME
        name_frame = Frame(waveform_frame)
        self._name_label = Label(name_frame, text=filename, justify="left", anchor="w")
        self._waveform_list_frame = Frame(waveform_frame)

        self._name_label.grid(sticky="nsew")

        for i in range(0, self._channels):
            waveform = SampleWaveform(self._waveform_list_frame, len(self._sound))
            waveform.pack(side="top", fill="both", expand=True)
            self._waveform_list.append(waveform)
        self._update_waveform()

        # WAVEFORM GRID

        name_frame.grid_rowconfigure(0, weight=1)
        name_frame.grid_columnconfigure(0, weight=1)

        name_frame.grid(row=0, sticky="nsew")
        self._waveform_list_frame.grid(row=1, sticky="nsew")

        waveform_frame.grid_rowconfigure(0, weight=1)
        waveform_frame.grid_rowconfigure(1, weight=1)

        # PACK ROOT

        settings_frame.pack(fill="y", side="left")
        waveform_frame.pack(fill="both", side="left")

    def _update_waveform(self):
        mono_segments = self._sound.split_to_mono()
        for i in range(0, self._channels):
            samples = mono_segments[i].get_array_of_samples()
            samples_array = np.array(samples).astype(np.float32)
            self._waveform_list[i].update_waveform(sound=samples_array, sample_rate=self._frame_rate)

    def _hide(self):
        if not self._is_hide:
            self._mute_button.grid_remove()
            self._solo_button.grid_remove()
            self._effects_button.grid_remove()
            self._gain_scale_frame.grid_remove()
            self._pan_scale_frame.grid_remove()
            self._waveform_list_frame.grid_remove()
            self._hide_button.configure(text="Показать")
            self._is_hide = True
        else:
            self._mute_button.grid()
            self._solo_button.grid()
            self._effects_button.grid()
            self._gain_scale_frame.grid()
            self._pan_scale_frame.grid()
            self._waveform_list_frame.grid()
            self._hide_button.configure(text="Скрыть")
            self._is_hide = False

    def _close(self):
        if not self._is_close and self.delete_allowed:
            self._root.destroy()
            self._is_close = True

    def _mute(self):
        self.set_mute(not self.is_mute())

    def _solo(self):
        self.set_solo(not self.is_solo())

    def _effects(self, start: int = None, end: int = None):
        segment = AudioSegment.empty()

        if start is None and end is None:
            segment = self._sound
        else:
            if start is None:
                segment = self._sound[:end]
            if end is None:
                segment = self._sound[start:]

        new_segment, flag = apply_effect(segment)
        if flag:
            self.sound = self._sound[:start] + new_segment + self._sound[end:]

    def is_close(self):
        return self._is_close

    def is_mute(self):
        return self._is_mute

    def is_solo(self):
        return self.solo_id == self.ID

    def is_hide(self):
        return self._is_hide

    def get_sound(self):
        if not self.is_mute():
            return self._sound.pan(self._pan.get() / 100) + self._gain.get()
        return AudioSegment.empty()

    def set_mute(self, state: bool):
        self._is_mute = state
        if state:
            self._mute_button.configure(relief="sunken")
        else:
            self._mute_button.configure(relief="raised")

    def set_solo(self, state: bool):
        if state:
            Sound.solo_id = self.ID
            self._solo_button.configure(relief="sunken")
        else:
            Sound.solo_id = -1
            self._solo_button.configure(relief="raised")

    def solo_tracking(self):
        if Sound.solo_id >= 0:
            if not self.is_solo():
                self.set_mute(True)
                return

        self.set_mute(False)

    def _msg_gain(self):
        return "Усиление: " + str(self._gain.get()) + " дБ"

    def _msg_pan(self):
        if self._pan.get() > 0:
            return "Баланс: " + str(self._pan.get()) + "% правый"
        if self._pan.get() < 0:
            return "Баланс: " + str(self._pan.get() * -1) + "% левый"
        return "Баланс: центр"

    def grid(self, row: int):
        self._root.grid(row=row, sticky="nsew", padx=2, pady=2)
