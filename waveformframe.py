import waveform as wf

from pydub import AudioSegment
from tkinter import Frame, Label
from tkinter.ttk import LabelFrame
from PIL import ImageTk


class WaveformFrame:
    def __init__(self, master: LabelFrame, sound: AudioSegment):
        waveform = [wf.Waveform(each) for each in sound]
        self.img = [ImageTk.PhotoImage(each.get_image()) for each in waveform]

        # WAVEFORM FRAME
        self.waveform_frame = Frame(master)
        self.waveform_frame.pack(side="left", expand=True)

        # VARIABLES
        for each in self.img:
            Label(self.waveform_frame, image=each, justify="left").pack(side="top", anchor="w")
