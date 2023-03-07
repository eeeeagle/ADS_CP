import waveform as wf

from tktooltip import ToolTip
from entrywindow import change_value
from PIL.ImageTk import PhotoImage
from pydub import AudioSegment
from tkinter.ttk import Frame, Scale, LabelFrame
from tkinter import Button, Label, Frame, DoubleVar, IntVar


class Sound:
    solo_pressed = False
    solo_id = -1

    mute_pressed = False
    mute_id = -1

    _id = 0

    def __init__(self, settings: Frame, filename: str):
        # VARIABLES
        self._audio_track_list = AudioSegment.from_file(filename, filename.split('.')[-1]).split_to_mono()

        self._gain = DoubleVar(value=0.0)
        self._pan = IntVar(value=0)

        self._is_close = False
        self._is_hide = False

        self._is_mute = False
        self._is_solo = False

        self._image_list = list[PhotoImage]()

        self.ID = Sound._id
        Sound._id += 1

        # ROOT
        self._root = Frame(settings, borderwidth=1, relief="solid")
        self.settings_frame = Frame(self._root, borderwidth=1, relief="solid")
        self.waveform_frame = Frame(self._root, borderwidth=1, relief="solid")

        # BUTTONS
        close_button = Button(self.settings_frame, text="Закрыть", justify="center", command=self._close)
        self.hide_button = Button(self.settings_frame, text="Скрыть", justify="center", command=self._hide)
        self.mute_button = Button(self.settings_frame, text="Тихо", justify="center", command=self._mute)
        self.solo_button = Button(self.settings_frame, text="Соло", justify="center", command=self._solo)
        self.effects_button = Button(self.settings_frame, text="Эффекты", justify="center", command=self._effects)

        # GAIN FRAME
        self.gain_scale_frame = LabelFrame(self.settings_frame, text="Усиление", labelanchor="n")
        self.gain_scale = Scale(self.gain_scale_frame, orient="horizontal", length=100, from_=-36.0, to=36.0,
                                variable=self._gain, command=lambda e: self._gain.set(value=round(float(e), 0)))
        self.gain_scale.pack(side="top", fill="both", expand=True)

        self.gain_scale_frame.bind("<Button-2>", func=lambda e: self._gain.set(value=0.0))
        self.gain_scale_frame.bind("<Double-Button-1>", lambda e: change_value("Усиление", self._gain, -36.0, 36.0))
        ToolTip(self.gain_scale_frame, msg=self._msg_gain)

        # PAN FRAME
        self.pan_scale_frame = LabelFrame(self.settings_frame, text="Баланс", labelanchor="n")
        self.pan_scale = Scale(self.pan_scale_frame, orient="horizontal", length=100, from_=-100, to=100,
                               variable=self._pan, command=lambda e: self._pan.set(value=round(float(e))))
        self.pan_scale.pack(side="top", fill="both", expand=True)
        self.pan_scale_frame.bind("<Button-2>", func=lambda e: self._pan.set(value=0))
        self.pan_scale_frame.bind("<Double-Button-1>", lambda e: change_value("Усиление", self._pan, -100, 100))
        ToolTip(self.pan_scale_frame, msg=self._msg_pan)

        # SETTINGS GRID
        close_button.grid(row=0, column=0, padx=2, pady=2, sticky="we")
        self.hide_button.grid(row=0, column=1, padx=2, pady=2, sticky="we")
        self.mute_button.grid(row=1, column=0, padx=2, pady=2, sticky="we")
        self.solo_button.grid(row=1, column=1, padx=2, pady=2, sticky="we")
        self.effects_button.grid(row=2, column=0, columnspan=2, padx=2, pady=2, sticky="we")
        self.gain_scale_frame.grid(row=3, column=0, columnspan=2, padx=2, pady=2, sticky="nsew")
        self.pan_scale_frame.grid(row=4, column=0, columnspan=2, padx=2, pady=2, sticky="nsew")

        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_frame.grid_columnconfigure(1, weight=1)

        # WAVEFORM FRAME
        self._image_list = list[PhotoImage]()
        self._label_list = list[Label]()

        name_frame = Frame(self.waveform_frame, borderwidth=1, relief="solid")

        self._name_label = Label(name_frame, text=filename, justify="left", anchor="w")
        self.image_frame = Frame(self.waveform_frame, borderwidth=1, relief="solid")

        self._name_label.grid(sticky="nsew")
        self.image_frame.grid(row=1, sticky="nsew")

        name_frame.grid(row=0, sticky="nsew")

        self.update_image_list(self._audio_track_list)

        # PACK ROOT

        self.settings_frame.pack(fill="y", side="left")
        self.waveform_frame.pack(fill="both", side="left", expand=True)
        self._root.grid(row=self.ID, sticky="nsew")

    def update_image_list(self, sound_list: list[AudioSegment]):
        self._image_list.clear()
        self._label_list.clear()

        waveform_list = [wf.Waveform(sound) for sound in sound_list]
        self._image_list = [PhotoImage(each.get_image()) for each in waveform_list]
        self._label_list = [Label(self.image_frame, image=image, justify="left") for image in self._image_list]

        for label in self._label_list:
            label.pack(side="top", anchor="w")

    def _hide(self):
        if not self._is_hide:
            self.mute_button.grid_remove()
            self.solo_button.grid_remove()
            self.effects_button.grid_remove()
            self.gain_scale_frame.grid_remove()
            self.pan_scale_frame.grid_remove()
            self.image_frame.pack_forget()
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
        if not self._is_close:
            self.settings_frame.destroy()
            self.waveform_frame.destroy()
            self._is_close = True

    def _mute(self):
        self.set_mute(not self._is_mute)

    def _solo(self):
        self.set_solo(not self._is_solo)

    def _effects(self):
        print(self.ID, end=": effects")

    def is_close(self):
        return self._is_close

    def is_mute(self):
        return self._is_mute

    def is_solo(self):
        return self._is_solo

    def is_hide(self):
        return self._is_hide

    def get_sound(self):
        if not self.is_mute():
            return AudioSegment.from_mono_audiosegments(*self._audio_track_list).pan(self._pan.get()) + self._gain.get()
        return AudioSegment.empty()

    def get_frames(self):
        return self.settings_frame, self.waveform_frame

    def set_mute(self, state: bool):
        if state:
            self.mute_button.configure(relief="sunken")
            self._is_mute = True
        else:
            self.mute_button.configure(relief="raised")
            self._is_mute = False

    def set_solo(self, state: bool):
        if state:
            Sound.solo_id = self.ID
            self.solo_button.configure(relief="sunken")
            self._is_mute = True
            self.set_mute(False)
        else:
            Sound.solo_id = -1
            self.solo_button.configure(relief="raised")
            self._is_solo = False

    def solo_tracking(self):
        if 0 <= Sound.solo_id != self.ID:
            self.set_mute(True)
        else:
            self.set_mute(False)

    def _msg_gain(self):
        return "Усиление: " + str(self._gain.get()) + " дБ"

    def _msg_pan(self):
        if self._pan.get() > 0.0:
            return "Баланс: " + str(round(self._pan.get())) + "% правый"
        if self._pan.get() < 0.0:
            return "Баланс: " + str(abs(round(self._pan.get()))) + "% левый"
        return "Баланс: центр"
