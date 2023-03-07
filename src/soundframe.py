from soundsettingsframe import SoundSettingsFrame
from waveformframe import WaveformFrame
from pydub import AudioSegment
from tkinter.ttk import Frame
from tkinter import Misc, Button, Label


class SoundFrame:
    _audio_track_list: list[AudioSegment]
    _is_close = False
    _is_hide = False

    def __init__(self, master: Misc, filename: str):
        self._audio_track_list = AudioSegment.from_file(filename, filename.split('.')[-1]).split_to_mono()

        # ROOT
        self._root = Frame(master, borderwidth=1, relief="solid")
        self._root.pack(side="top", fill="both", padx=2, pady=2)

        # CONTROL FRAME
        control_frame = Frame(self._root, borderwidth=1, relief="solid")
        delete_sound_button = Button(control_frame, text="Закрыть", justify="center", command=self._close)
        self._hide_sound_button = Button(control_frame, text="Скрыть", justify="center", command=self._hide)

        delete_sound_button.grid(row=0, column=0, padx=2, pady=2, sticky="we")
        self._hide_sound_button.grid(row=0, column=1, padx=2, pady=2, sticky="we")

        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)

        # LABEL FRAME
        label_frame = Frame(self._root, borderwidth=1, relief="solid")
        self._filename_label = Label(label_frame, text=filename, justify="left", anchor="w")

        self._filename_label.pack(side="left", fill="both")

        # SOUND FRAMES
        self._sound_settings_frame = SoundSettingsFrame(self._root)
        self._sound_waveform_frame = WaveformFrame(self._root, self._audio_track_list)

        # ROOT GRID
        control_frame.grid(row=0, column=0, sticky="nsew")
        label_frame.grid(row=0, column=1, sticky="nsew")
        self._sound_settings_frame.grid(row=1, column=0, sticky="nsew")
        self._sound_waveform_frame.grid(row=1, column=1, sticky="nsew")

        self._root.grid_columnconfigure(1, weight=1)

    def _hide(self):
        if not self._is_hide:
            self._sound_settings_frame.grid_remove()
            self._sound_waveform_frame.grid_remove()
            self._hide_sound_button.configure(text="Показать")
            self._is_hide = True
        else:
            self._sound_settings_frame.grid_show()
            self._sound_waveform_frame.grid_show()
            self._hide_sound_button.configure(text="Скрыть")
            self._is_hide = False

    def _close(self):
        if not self._is_close:
            self._is_close = True
            self._root.destroy()

    def get_root(self):
        return self._root

    def is_close(self):
        return self._is_close

    def is_muted(self):
        return self._sound_settings_frame.is_muted()

    def get_sound(self):
        if not self.is_muted():
            return AudioSegment.from_mono_audiosegments(*self._audio_track_list) + self._sound_settings_frame.get_gain()
        return AudioSegment.empty()
