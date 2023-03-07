import os.path
import simpleaudio as sa
import threading

from soundframe import SoundFrame
from tkinter.ttk import Label, LabelFrame, Scale, Combobox
from tkinter import Tk, IntVar, StringVar, Frame, Button, Canvas, Scrollbar, Menu, messagebox, filedialog
from tktooltip import ToolTip
from pydub import AudioSegment
from ctypes import *
from entrywindow import change_value

from time import sleep


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
    _status: StringVar
    _volume: IntVar
    _samplerate: IntVar
    _active_thread = list()
    _on_exit = False

    def __init__(self, master: Tk):
        """MASTER = base object"""

        """ VARIABLES """
        self._volume = IntVar(value=0)
        self._samplerate = IntVar(value=SAMPLERATE_LIST[5])
        self._status = StringVar(value="")

        """ MAIN MENU """
        main_menu = Menu(master)
        master.config(menu=main_menu)

        file_menu = Menu(main_menu, tearoff=0)
        help_menu = Menu(main_menu, tearoff=0)

        file_menu.add_command(label="Импорт файлов", command=self._open_files)
        file_menu.add_command(label="Экспорт", command=self._save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=master.destroy)

        help_menu.add_command(label="Помощь")
        help_menu.add_command(label="О программе")

        main_menu.add_cascade(label="Файл", menu=file_menu)
        main_menu.add_cascade(label="Справка", menu=help_menu)

        """ TOOLBAR FRAME """
        toolbar_frame = Frame(master, borderwidth=1, relief="ridge")
        toolbar_frame.pack(side="top", padx=2, pady=2, fill="x")

        """ SOUND FRAME """
        sound_frame = Frame(master)
        sound_frame.pack(side="top", fill="both", expand=True)

        sound_frame_canvas = Canvas(sound_frame, background="#3a3a58")
        self._sound_frame_canvas_frame = Frame(sound_frame_canvas, background="#3a3a58")
        self._sound_frame_canvas_frame.grid(sticky="nsew")

        sound_frame_scrollbar_x = Scrollbar(sound_frame, orient="horizontal", command=sound_frame_canvas.xview)
        sound_frame_scrollbar_y = Scrollbar(sound_frame, orient="vertical", command=sound_frame_canvas.yview)
        sound_frame_canvas.configure(xscrollcommand=sound_frame_scrollbar_x.set,
                                     yscrollcommand=sound_frame_scrollbar_y.set)

        sound_frame_canvas.grid(row=0, column=0, sticky="nsew")
        sound_frame_scrollbar_x.grid(column=0, row=1, sticky="ew")
        sound_frame_scrollbar_y.grid(column=1, row=0, sticky="ns")

        sound_frame.columnconfigure(0, weight=1)
        sound_frame.rowconfigure(0, weight=1)

        sound_frame_canvas.create_window((0, 0), window=self._sound_frame_canvas_frame, anchor="nw")

        self._sound_frame_canvas_frame.bind(
            "<Configure>",
            lambda e: sound_frame_canvas.configure(scrollregion=sound_frame_canvas.bbox("all"))
        )

        sound_frame_canvas.bind(
            "<Configure>",
            lambda e: sound_frame_canvas.itemconfig("scrollable", width=e.width, height=e.height)
        )

        """ TOOLBAR: PLAY FRAME"""
        play_frame = Frame(toolbar_frame)
        play_button = Button(play_frame, text="Играть", command=self._play_sound)
        pause_button = Button(play_frame, text="Пауза", command=self._pause_sound)
        stop_button = Button(play_frame, text="Стоп", command=sa.stop_all)
        record_button = Button(play_frame, text="Запись", command=self._record_sound)

        play_frame.pack(side="left", padx=2)
        play_button.pack(side="left", fill="both", padx=2, pady=2)
        pause_button.pack(side="left", fill="both", padx=2, pady=2)
        stop_button.pack(side="left", fill="both", padx=2, pady=2)
        record_button.pack(side="left", fill="both", padx=2, pady=2)

        """ TOOLBAR: VOLUME LABEL FRAME"""
        volume_frame = LabelFrame(toolbar_frame, text="Громкость", labelanchor="n")
        volume_frame.pack(side="right", fill="y", padx=2)

        volume_scale = Scale(volume_frame, orient="horizontal", length=100, from_=-50.0, to=0.0,
                             variable=self._volume,
                             command=lambda s: self._volume.set(value=round(float(s))))
        volume_scale.pack(padx=2, pady=2)
        volume_scale.bind("<Button-2>", func=lambda e: self._volume.set(value=0))
        volume_scale.bind("<Double-Button-1>", lambda e: change_value("Громкость", self._volume, -50, 0))
        ToolTip(volume_scale, msg=self._msg_volume, delay=0)

        """ TOOLBAR: SAMPLERATE FRAME"""
        samplerate_frame = LabelFrame(toolbar_frame, text="Частота дискретизации", labelanchor="n")
        samplerate_frame.pack(side="right", fill="y", padx=2)

        samplerate_combobox = Combobox(samplerate_frame, values=SAMPLERATE_LIST,
                                       textvariable=self._samplerate, state="readonly")
        samplerate_combobox.current(5)
        samplerate_combobox.pack(fill="both", padx=2, pady=2)

        """ STATUS BAR FRAME"""
        status_bar_frame = Frame(master, borderwidth=1, relief="ridge")
        self._status_bar_label = Label(status_bar_frame, textvariable=self._status)

        status_bar_frame.pack(side="bottom", fill="x")
        self._status_bar_label.pack(side="left")

        thread_collect_closed = threading.Thread(target=self._closed_sound_collector, args=())
        thread_collect_closed.start()

    def __del__(self):
        sa.stop_all()
        self._on_exit = True

    def _closed_sound_collector(self):
        while not self._on_exit:
            for sound in self._sound_frame_list:
                if sound.is_close():
                    self._sound_frame_list.remove(sound)
            sleep(1)

    def _msg_volume(self):
        return "Громоксть воспроизведения: " + str(self._volume.get()) + " дБ"

    def _open_files(self):
        filepath = filedialog.askopenfilenames(title="Выберите один или несколько файлов", filetypes=EXTENSION_LIST)

        if filepath != "":
            for sound in filepath:
                self._sound_frame_list.append(SoundFrame(self._sound_frame_canvas_frame, sound))

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
            self._status.set("Остановленно")
            self._active_thread.remove(thread)

        sa.stop_all()

        sound_list = self._get_active_sound()
        if len(sound_list):
            sound = overlay_sounds(sound_list, self._samplerate.get()) + self._volume.get()
            play_object = sa.play_buffer(sound.raw_data, num_channels=sound.channels,
                                         bytes_per_sample=sound.sample_width, sample_rate=sound.frame_rate)
            self._status.set("Играет")

            thread = threading.Thread(target=wait_play, args=())
            thread.start()
            self._active_thread.append(thread)
        else:
            messagebox.showinfo(title="Воспроизведение невозможно", message="Нет аудио для воспроизведения")

    def _record_sound(self):
        print("Record")

    def _pause_sound(self):
        print("Pause")

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
