from soundsettingsframe import SoundSettingsFrame
from waveformframe import WaveformFrame
from pydub import AudioSegment
from tkinter.ttk import LabelFrame
from tkinter import Misc


class SoundFrame:
    def __init__(self, master: Misc, filepath: str):
        """
        master = base object;

        filepath = path to audio object
        """
        # VARIABLES
        self.sound = AudioSegment.from_file(filepath, filepath.split('.')[-1]).split_to_mono()

        # ROOT FRAME
        self.root = LabelFrame(master, text=filepath, labelanchor="nw", borderwidth=1, relief="solid")
        self.root.pack(side="top", anchor="nw", expand=True, padx=2, pady=2)
        self.root.bind()

        # CHILD FRAMES
        self.sound_settings_frame = SoundSettingsFrame(self.root)
        self.sound_waveform_frame = WaveformFrame(self.root, self.sound)

    def get_sound(self):
        return AudioSegment.from_mono_audiosegments(self.sound) + self.sound_settings_frame.get_gain()

    def is_muted(self):
        return self.sound_settings_frame.is_muted()
