import waveform as wf

from tktooltip import ToolTip
from entrywindow import change_value
from PIL.ImageTk import PhotoImage
from pydub import AudioSegment
from tkinter.ttk import Frame, Scale, LabelFrame
from tkinter import Button, Label, Frame, DoubleVar, IntVar


class Sound:
    solo_id = -1
    delete_allowed = True
    _id = 0

    def __init__(self, master: Frame, filename: str):
        # VARIABLES
        self._audio_track_list = AudioSegment.from_file(filename, filename.split('.')[-1]).split_to_mono()

        self._gain = DoubleVar(value=0.0)
        self._pan = IntVar(value=0)

        self._is_close = False
        self._is_hide = False
        self._is_mute = False

        self._image_list = list[PhotoImage]()

        self.ID = Sound._id
        Sound._id += 1

        # ROOT
        self._root = Frame(master)
        settings_frame = Frame(self._root, borderwidth=1, relief="solid")
        waveform_frame = Frame(self._root, borderwidth=1, relief="solid")

        # BUTTONS
        close_button = Button(settings_frame, text="Закрыть", justify="center", command=self._close)
        self.hide_button = Button(settings_frame, text="Скрыть", justify="center", command=self._hide)
        self.mute_button = Button(settings_frame, text="Тихо", justify="center", command=self._mute)
        self.solo_button = Button(settings_frame, text="Соло", justify="center", command=self._solo)
        self.effects_button = Button(settings_frame, text="Эффекты", justify="center", command=self._effects)

        # GAIN FRAME
        self.gain_scale_frame = LabelFrame(settings_frame, text="Усиление", labelanchor="n")
        self.gain_scale = Scale(self.gain_scale_frame, orient="horizontal", length=100, from_=-36.0, to=36.0,
                                variable=self._gain, command=lambda e: self._gain.set(value=round(float(e), 0)))
        self.gain_scale.pack(side="top", fill="both", expand=True)

        self.gain_scale.bind("<Button-2>", func=lambda e: self._gain.set(value=0.0))
        self.gain_scale.bind("<Double-Button-1>", lambda e: change_value("Усиление", self._gain, -36.0, 36.0))
        ToolTip(self.gain_scale, msg=self._msg_gain)

        # PAN FRAME
        self.pan_scale_frame = LabelFrame(settings_frame, text="Баланс", labelanchor="n")
        self.pan_scale = Scale(self.pan_scale_frame, orient="horizontal", length=100, from_=-100, to=100,
                               variable=self._pan, command=lambda e: self._pan.set(value=round(float(e))))
        self.pan_scale.pack(side="top", fill="both", expand=True)
        self.pan_scale.bind("<Button-2>", func=lambda e: self._pan.set(value=0))
        self.pan_scale.bind("<Double-Button-1>", lambda e: change_value("Усиление", self._pan, -100, 100))
        ToolTip(self.pan_scale, msg=self._msg_pan)

        # SETTINGS GRID
        close_button.grid(row=0, column=0, padx=2, pady=2, sticky="we")
        self.hide_button.grid(row=0, column=1, padx=2, pady=2, sticky="we")
        self.mute_button.grid(row=1, column=0, padx=2, pady=2, sticky="we")
        self.solo_button.grid(row=1, column=1, padx=2, pady=2, sticky="we")
        self.effects_button.grid(row=2, column=0, columnspan=2, padx=2, pady=2, sticky="we")
        self.gain_scale_frame.grid(row=3, column=0, columnspan=2, padx=2, pady=2, sticky="nsew")
        self.pan_scale_frame.grid(row=4, column=0, columnspan=2, padx=2, pady=2, sticky="nsew")

        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(1, weight=1)

        # WAVEFORM FRAME
        self._image_list = list[PhotoImage]()
        self._label_list = list[Label]()

        name_frame = Frame(waveform_frame)
        self._name_label = Label(name_frame, text=filename, justify="left", anchor="w")

        self.image_frame = Frame(waveform_frame)

        self._name_label.grid(sticky="nsew")
        self._update_image_list(self._audio_track_list)

        name_frame.grid_rowconfigure(0, weight=1)
        name_frame.grid_columnconfigure(0, weight=1)

        name_frame.grid(row=0, sticky="nsew")
        self.image_frame.grid(row=1, sticky="nsew")

        waveform_frame.grid_rowconfigure(0, weight=1)
        waveform_frame.grid_rowconfigure(1, weight=1)

        # PACK ROOT

        settings_frame.pack(fill="y", side="left")
        waveform_frame.pack(fill="both", side="left")

    def _update_image_list(self, sound_list: list[AudioSegment]):
        self._image_list.clear()
        self._label_list.clear()

        waveform_list = [wf.Waveform(sound) for sound in sound_list]
        self._image_list = [PhotoImage(each.get_image()) for each in waveform_list]
        self._label_list = [Label(self.image_frame, image=image, justify="left", borderwidth=1, relief="solid")
                            for image in self._image_list]

        for label in self._label_list:
            label.pack(side="top", anchor="w", expand=True)

    def _hide(self):
        if not self._is_hide:
            self.mute_button.grid_remove()
            self.solo_button.grid_remove()
            self.effects_button.grid_remove()
            self.gain_scale_frame.grid_remove()
            self.pan_scale_frame.grid_remove()
            self.image_frame.grid_remove()
            self.hide_button.configure(text="Показать")
            self._is_hide = True
        else:
            self.mute_button.grid()
            self.solo_button.grid()
            self.effects_button.grid()
            self.gain_scale_frame.grid()
            self.pan_scale_frame.grid()
            self.image_frame.grid()
            self.hide_button.configure(text="Скрыть")
            self._is_hide = False

    def _close(self):
        if not self._is_close and self.delete_allowed:
            self._root.destroy()
            self._is_close = True

    def _mute(self):
        self.set_solo(not self.is_solo())
        self.set_mute(not self._mute)

    def _solo(self):
        self.set_solo(not self.is_solo())

    def _effects(self):
        print(self.ID, end=": effects\n")

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
            audio = AudioSegment.from_mono_audiosegments(*self._audio_track_list)
            audio = audio.pan(self._pan.get() / 100)
            return audio + self._gain.get()
        return AudioSegment.empty()

    def set_mute(self, state: bool):
        if state:
            self._is_mute = True
            self.mute_button.configure(relief="sunken")
        else:
            self._is_mute = False
            self.mute_button.configure(relief="raised")

    def set_solo(self, state: bool):
        if state:
            Sound.solo_id = self.ID
            self.solo_button.configure(relief="sunken")
        else:
            Sound.solo_id = -1
            self.solo_button.configure(relief="raised")

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
