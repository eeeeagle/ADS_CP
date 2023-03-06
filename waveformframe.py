import waveform as wf

from pydub import AudioSegment
from tkinter import Frame, Label
from PIL.ImageTk import PhotoImage


class WaveformFrame:
    _image_list = list[PhotoImage]()
    _label_list = list[Label]()

    def __init__(self, master: Frame, sound_list: list[AudioSegment]):
        self.root = Frame(master, borderwidth=1, relief="solid")
        self.update_image_list(sound_list)

    def update_image_list(self, sound_list: list[AudioSegment]):
        self._image_list.clear()
        self._label_list.clear()

        waveform_list = [wf.Waveform(sound) for sound in sound_list]
        self._image_list = [PhotoImage(each.get_image()) for each in waveform_list]
        self._label_list = [Label(self.root, image=image, justify="left") for image in self._image_list]

        for label in self._label_list:
            label.pack(side="top", anchor="w")
