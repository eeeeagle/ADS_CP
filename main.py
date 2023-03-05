import os.path
import simpleaudio as sa

from soundframe import SoundFrame
from tkinter.ttk import Label, LabelFrame, Scale, Combobox
from tkinter import Tk, IntVar, Frame, Button, Canvas, Scrollbar, Menu, messagebox, filedialog
from tktooltip import ToolTip
from pydub import AudioSegment
from ctypes import *


SCREEN_WIDTH = windll.user32.GetSystemMetrics(0)
SCREEN_HEIGHT = windll.user32.GetSystemMetrics(1)
SAMPLERATE_LIST = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000, 352800, 384000]
EXTENSION_LIST = [("Все поддерживаемые форматы", ".wav .flac .m4a .mp3 .ogg"),
                  ("Microsoft Wave", ".wav"), ("Free Lossless Audio Codec", ".flac"), ("Apple Lossless", ".m4a"),
                  ("MPEG Layer 3", ".mp3"), ("Ogg Vorbis Audio", ".ogg")]


def stop_sound():
    sa.stop_all()


def overlay_sounds(sound_list: list[AudioSegment], samplerate: int):
    output_sound = AudioSegment.silent(duration=max([len(sound) for sound in sound_list]), frame_rate=samplerate)
    for sound in sound_list:
        output_sound = output_sound.overlay(sound)
    return output_sound


class MainApp:
    def __init__(self, master):
        """MASTER = base object"""

        """ VARIABLES """
        self.soundframe_list = list[SoundFrame]()
        self.volume = IntVar(value=0)
        self.samplerate = IntVar(value=SAMPLERATE_LIST[5])

        """ TOOLBAR FRAME """
        self.toolbar_frame = Frame(master, borderwidth=1, relief="ridge")
        self.toolbar_frame.pack(side="top", padx=2, pady=2, fill="x")

        """ SOUND FRAME """
        self.sound_frame = Frame(master)
        self.sound_frame.pack(side="top", fill="both", expand=True)

        self.sound_frame_canvas = Canvas(self.sound_frame)
        self.sound_frame_canvas_frame = Frame(self.sound_frame_canvas)
        self.sound_frame_canvas_frame.grid(sticky="nsew")

        self.sound_frame_scrollbar_x = Scrollbar(self.sound_frame, orient="horizontal")
        self.sound_frame_scrollbar_y = Scrollbar(self.sound_frame, orient="vertical",
                                                 command=self.sound_frame_canvas.yview)
        self.sound_frame_canvas.configure(yscrollcommand=self.sound_frame_scrollbar_y.set)

        self.sound_frame_canvas.grid(row=0, column=0, sticky="nsew")
        self.sound_frame_scrollbar_x.grid(column=0, row=1, sticky="ew")
        self.sound_frame_scrollbar_y.grid(column=1, row=0, sticky="ns")

        self.sound_frame.columnconfigure(0, weight=1)
        self.sound_frame.rowconfigure(0, weight=1)

        self.sound_frame_canvas.create_window((0, 0), window=self.sound_frame_canvas_frame, anchor="nw")

        self.sound_frame_canvas_frame.bind(
            "<Configure>",
            lambda e: self.sound_frame_canvas.configure(scrollregion=self.sound_frame_canvas.bbox("all")))

        self.sound_frame_canvas.bind(
            "<Configure>",
            lambda e: self.sound_frame_canvas.itemconfig("scrollable", width=e.width, height=e.height))

        """ STATUS BAR FRAME"""
        self.status_bar_frame = Frame(master, borderwidth=1, relief="ridge")
        self.status_bar_frame.pack(side="bottom", padx=2, pady=2, fill="x")

        self.status_bar_label = Label(self.status_bar_frame, text="text")
        self.status_bar_label.pack(side="left")

        """ PLAY FRAME"""
        self.play_frame = Frame(self.toolbar_frame)
        self.play_frame.pack(side="left", padx=2)

        """ VOLUME FRAME"""
        self.volume_frame = LabelFrame(self.toolbar_frame, text="Громкость (dB)", labelanchor="n")
        self.volume_frame.pack(side="right", padx=2)

        """ SAMPLERATE FRAME"""
        self.samplerate_frame = Frame(self.toolbar_frame)
        self.samplerate_frame.pack(side="right", padx=2)

        """ PLAY BUTTON"""
        self.play_button = Button(self.play_frame, text="Играть", command=self._play_sound)
        self.play_button.pack(side="top", fill="both", padx=2, pady=2)

        """ STOP BUTTON"""
        self.stop_button = Button(self.play_frame, text="Стоп", command=stop_sound)
        self.stop_button.pack(side="top", fill="both", padx=2, pady=2)

        """ VOLUME SCALE"""
        self.volume_scale = Scale(self.volume_frame, orient="horizontal", length=100, from_=-50.0, to=0.0,
                                  variable=self.volume,
                                  command=lambda s: self.volume.set(value=round(float(s))))
        self.volume_scale.pack(padx=2, pady=2)

        ToolTip(self.volume_scale, msg=self._msg_volume, delay=0)

        """ SAMPLE RATE COMBOBOX"""
        self.samplerate_label = Label(self.samplerate_frame, text="Sample Rate", justify="center")
        self.samplerate_label.pack(anchor="n")

        self.samplerate_combobox = Combobox(self.samplerate_frame, width=7, values=SAMPLERATE_LIST,
                                            textvariable=self.samplerate, state="readonly")
        self.samplerate_combobox.current(5)
        self.samplerate_combobox.pack(padx=2, pady=2)

        """ MAIN MENU """
        self.main_menu = Menu(master)
        master.config(menu=self.main_menu)

        self.file_menu = Menu(self.main_menu, tearoff=0)
        self.help_menu = Menu(self.main_menu, tearoff=0)

        self.file_menu.add_command(label="Импорт файлов", command=self._open_files)
        self.file_menu.add_command(label="Экспорт", command=self._save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Выход", command=master.destroy)

        self.help_menu.add_command(label="Помощь")
        self.help_menu.add_command(label="О программе")

        self.main_menu.add_cascade(label="Файл", menu=self.file_menu)
        self.main_menu.add_cascade(label="Справка", menu=self.help_menu)

    def _msg_volume(self):
        return "Громоксть воспроизведения: " + str(self.volume.get()) + " дБ"

    def _open_files(self):
        filepath = filedialog.askopenfilenames(title="Выберите один или несколько файлов", filetypes=EXTENSION_LIST)

        if filepath != "":
            for sound in filepath:
                self.soundframe_list.append(SoundFrame(self.sound_frame_canvas_frame, sound))

    def _save_file(self):
        filepath = filedialog.asksaveasfilename(title="Экспорт аудиоданных", defaultextension=EXTENSION_LIST[1][1],
                                                initialfile="Song", filetypes=EXTENSION_LIST[1:])
        sound_list = [sound.get_sound() for sound in self.soundframe_list]
        if filepath != "":
            sound = overlay_sounds(sound_list, self.samplerate.get())
            sound.export(filepath, format=os.path.splitext(filepath)[1][1:])

    def _play_sound(self):
        stop_sound()
        sound_list = self._get_active_sound()
        if len(sound_list):
            sound = overlay_sounds(sound_list, self.samplerate.get()) + self.volume.get()
            sa.play_buffer(sound.raw_data, num_channels=sound.channels,
                           bytes_per_sample=sound.sample_width, sample_rate=sound.frame_rate)
        else:
            messagebox.showinfo(title="Воспроизведение невозможно", message="Нет аудио для воспроизведения")

    def _get_active_sound(self):
        sound_list = list()
        for sound in self.soundframe_list:
            if not sound.is_muted():
                sound_list.append(sound.get_sound())
        return sound_list


if __name__ == "__main__":
    root = Tk()
    root.iconbitmap(default="icon.ico")
    root.title("Аудио редактор")
    root.geometry(str(int(SCREEN_WIDTH * 0.7)) + "x" + str(int(SCREEN_HEIGHT * 0.7)) +
                  "+" + str(int(SCREEN_WIDTH * 0.15)) + "+" + str(int(SCREEN_HEIGHT * 0.15)))

    app = MainApp(root)
    root.mainloop()
