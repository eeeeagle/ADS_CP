import waveform as wf

from pydub import AudioSegment
from tkinter import Frame, Label
from tkinter.ttk import LabelFrame
from PIL import ImageTk


class WaveformFrame:
    def __init__(self, master: LabelFrame, sound: AudioSegment):
        # VARIABLES
        waveform = wf.Waveform(sound)
        self.img = ImageTk.PhotoImage(waveform.get_image())

        # WAVEFORM FRAME
        self.waveform_frame = Frame(master)
        self.waveform_frame.pack(side="left")

        self.waveform_frame_label = Label(self.waveform_frame, image=self.img, justify="left")
        self.waveform_frame_label.pack(anchor="w")
