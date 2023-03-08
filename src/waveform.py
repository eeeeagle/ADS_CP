import tkinter as tk
import librosa.display

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SampleWaveform(tk.Frame):
    def __init__(self, master: tk.Misc, sound, sample_rate):
        super().__init__(master)

        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.pack(fill="both")

        self.fig = Figure(figsize=(len(sound) / sample_rate / 20, 2), dpi=100)
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax = self.fig.add_subplot()

        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)

        self.canvas = FigureCanvasTkAgg(self.fig, self.canvas_frame)
        self.canvas.get_tk_widget().grid(column=0, row=0, sticky="nsew")

        self.adaptor = librosa.display.waveshow(sound, sr=sample_rate, ax=self.ax, axis="s", lw=0.5, zorder=1)

        self.ax.set_xlim(0, len(sound) / sample_rate)
        self.canvas.draw()
        self.bg = self.canvas.copy_from_bbox(self.ax.bbox)

    def destroy(self):
        return super().destroy()
