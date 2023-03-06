import os.path
import simpleaudio as sa
import threading

from soundframe import SoundFrame
from tkinter.ttk import Label, LabelFrame, Scale, Combobox
from tkinter import Tk, IntVar, Frame, Button, Canvas, Scrollbar, Menu, messagebox, filedialog
from tktooltip import ToolTip
from pydub import AudioSegment
from ctypes import *
from entrywindow import EntryWindow


SCREEN_WIDTH = windll.user32.GetSystemMetrics(0)
SCREEN_HEIGHT = windll.user32.GetSystemMetrics(1)
SAMPLERATE_LIST = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000, 352800, 384000]
EXTENSION_LIST = [("Все поддерживаемые форматы", ".wav .flac .m4a .mp3 .ogg"),
                  ("Microsoft Wave", ".wav"), ("Free Lossless Audio Codec", ".flac"), ("Apple Lossless", ".m4a"),
                  ("MPEG Layer 3", ".mp3"), ("Ogg Vorbis Audio", ".ogg")]


def overlay_sounds(sound_list: list[AudioSegment], samplerate: int):
    output_sound = AudioSegment.silent(duration=max([len(sound) for sound in sound_list]), frame_rate=samplerate)
    for sound in sound_list:
        output_sound = output_sound.overlay(sound)
    return output_sound


class MainApp:
    _sound_frame_list = list[SoundFrame]()
    _volume: IntVar
    _samplerate: IntVar

    def __init__(self, master: Tk):
        """MASTER = base object"""

        """ VARIABLES """
        self._volume = IntVar(value=0)
        self._samplerate = IntVar(value=SAMPLERATE_LIST[5])

        """ TOOLBAR FRAME """
        self._toolbar_frame = Frame(master, borderwidth=1, relief="ridge")
        self._toolbar_frame.pack(side="top", padx=2, pady=2, fill="x")
        self._toolbar_frame.bind("Destroy", self.__del__)

        """ SOUND FRAME """
        self._sound_frame = Frame(master, background="red")
        self._sound_frame.pack(side="top", fill="both", expand=True)

        self.sound_frame_canvas = Canvas(self._sound_frame, background="red")
        self.sound_frame_canvas_frame = Frame(self.sound_frame_canvas, background="red")
        self.sound_frame_canvas_frame.grid(sticky="nsew")

        self.sound_frame_scrollbar_x = Scrollbar(self._sound_frame, orient="horizontal",
                                                 command=self.sound_frame_canvas.xview)
        self.sound_frame_scrollbar_y = Scrollbar(self._sound_frame, orient="vertical",
                                                 command=self.sound_frame_canvas.yview)
        self.sound_frame_canvas.configure(xscrollcommand=self.sound_frame_scrollbar_x.set,
                                          yscrollcommand=self.sound_frame_scrollbar_y.set)

        self.sound_frame_canvas.grid(row=0, column=0, sticky="nsew")
        self.sound_frame_scrollbar_x.grid(column=0, row=1, sticky="ew")
        self.sound_frame_scrollbar_y.grid(column=1, row=0, sticky="ns")

        self._sound_frame.columnconfigure(0, weight=1)
        self._sound_frame.rowconfigure(0, weight=1)

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

        self.status_bar_label = Label(self.status_bar_frame, text="")
        self.status_bar_label.pack(side="left")

        """ PLAY FRAME"""
        self.play_frame = Frame(self._toolbar_frame)
        self.play_frame.pack(side="left", padx=2)

        """ VOLUME FRAME"""
        self.volume_frame = LabelFrame(self._toolbar_frame, text="Громкость", labelanchor="n")
        self.volume_frame.pack(side="right", fill="y", padx=2)

        """ SAMPLERATE FRAME"""
        self.samplerate_frame = LabelFrame(self._toolbar_frame, text="Частота дискретизации", labelanchor="n")
        self.samplerate_frame.pack(side="right", fill="y", padx=2)

        """ PLAY BUTTON"""
        self.play_button = Button(self.play_frame, text="Играть", command=self._play_sound)
        self.play_button.pack(side="top", fill="both", padx=2, pady=2)

        """ STOP BUTTON"""
        self.stop_button = Button(self.play_frame, text="Стоп", command=sa.stop_all)
        self.stop_button.pack(side="top", fill="both", padx=2, pady=2)

        """ VOLUME SCALE"""
        self.volume_scale = Scale(self.volume_frame, orient="horizontal", length=100, from_=-50.0, to=0.0,
                                  variable=self._volume,
                                  command=lambda s: self._volume.set(value=round(float(s))))
        self.volume_scale.pack(padx=2, pady=2)
        self.volume_scale.bind("<Button-2>", func=lambda e: self._volume.set(value=0))
        self.volume_scale.bind("<Double-Button-1>", lambda e: self._change_volume())
        ToolTip(self.volume_scale, msg=self._msg_volume, delay=0)

        """ SAMPLE RATE COMBOBOX"""
        self.samplerate_combobox = Combobox(self.samplerate_frame, values=SAMPLERATE_LIST,
                                            textvariable=self._samplerate, state="readonly")
        self.samplerate_combobox.current(5)
        self.samplerate_combobox.pack(fill="both", padx=2, pady=2)

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

    def __del__(self):
        sa.stop_all()

    def _closed_sound_collector(self):
        for i in range(0, len(self._sound_frame_list)):
            if self._sound_frame_list[i].is_close():
                self._sound_frame_list.pop(i)

    def _change_volume(self):
        def extra_window():
            window = EntryWindow("Громкость", self._volume.get(), -50, 0)
            self._volume.set(value=window.value)

        thr = threading.Thread(target=extra_window, args=())
        thr.start()

    def _msg_volume(self):
        return "Громоксть воспроизведения: " + str(self._volume.get()) + " дБ"

    def _open_files(self):
        filepath = filedialog.askopenfilenames(title="Выберите один или несколько файлов", filetypes=EXTENSION_LIST)

        if filepath != "":
            for sound in filepath:
                self._sound_frame_list.append(SoundFrame(self.sound_frame_canvas_frame, sound))

    def _save_file(self):
        filepath = filedialog.asksaveasfilename(title="Экспорт аудиоданных", defaultextension=EXTENSION_LIST[1][1],
                                                initialfile="Song", filetypes=EXTENSION_LIST[1:])
        sound_list = [sound.get_sound() for sound in self._sound_frame_list]
        if filepath != "":
            sound = overlay_sounds(sound_list, self._samplerate.get())
            sound.export(filepath, format=os.path.splitext(filepath)[1][1:])

    def _play_sound(self):
        def wait_play():
            play_object.wait_done()
            self.status_bar_label.configure(text="Остановленно")

        sa.stop_all()

        self._closed_sound_collector()

        sound_list = self._get_active_sound()
        if len(sound_list):
            sound = overlay_sounds(sound_list, self._samplerate.get()) + self._volume.get()
            play_object = sa.play_buffer(sound.raw_data, num_channels=sound.channels,
                                         bytes_per_sample=sound.sample_width, sample_rate=sound.frame_rate)
            self.status_bar_label.configure(text="Играет")

            wait_play_thread = threading.Thread(target=wait_play, args=())
            wait_play_thread.start()
        else:
            messagebox.showinfo(title="Воспроизведение невозможно", message="Нет аудио для воспроизведения")

    def _get_active_sound(self):
        sound_list = list()
        for sound in self._sound_frame_list:
            sound_list.append(sound.get_sound())
        return sound_list

    def is_empty(self):
        return len(self._sound_frame_list) == 0


if __name__ == "__main__":
    def on_exit():
        if app.is_empty() or messagebox.askokcancel("Выход", "Вы действительно хотите выйти?"):
            sa.stop_all()
            root.destroy()

    root = Tk()
    root.iconbitmap(default="icon.ico")
    root.title("Аудио редактор")
    root.geometry(str(int(SCREEN_WIDTH * 0.7)) + "x" + str(int(SCREEN_HEIGHT * 0.7)) +
                  "+" + str(int(SCREEN_WIDTH * 0.15)) + "+" + str(int(SCREEN_HEIGHT * 0.15)))

    root.protocol("WM_DELETE_WINDOW", on_exit)

    app = MainApp(root)
    root.mainloop()
