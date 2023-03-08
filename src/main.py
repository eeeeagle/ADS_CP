import os.path
import simpleaudio as sa
import threading

from tkinter.ttk import Label, LabelFrame, Scale, Combobox
from tkinter import Tk, IntVar, StringVar, Frame, Button, Menu, messagebox, filedialog
from tktooltip import ToolTip
from pydub import AudioSegment
from ctypes import *
from entrywindow import change_value
from tkscrolledframe import ScrolledFrame
from sound import Sound
from time import sleep


SCREEN_WIDTH = windll.user32.GetSystemMetrics(0)
SCREEN_HEIGHT = windll.user32.GetSystemMetrics(1)
SAMPLERATE_LIST = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000, 352800, 384000]
EXTENSION_LIST = [("Все поддерживаемые форматы", ".wav .flac .m4a .mp3 .ogg"),
                  ("Microsoft Wave", ".wav"), ("Free Lossless Audio Codec", ".flac"), ("Apple Lossless", ".m4a"),
                  ("MPEG Layer 3", ".mp3"), ("Ogg Vorbis Audio", ".ogg")]
BG_COLOR = "#3a3a58"


def overlay_sounds(sound_list: list[AudioSegment], samplerate: int):
    output_sound = AudioSegment.silent(duration=max([len(sound) for sound in sound_list]), frame_rate=samplerate)
    for sound in sound_list:
        output_sound = output_sound.overlay(sound)
    return output_sound


class MainApp:
    def __init__(self, master: Tk):
        """MASTER = base object"""

        """ VARIABLES """
        self._volume = IntVar(value=0)
        self._samplerate = IntVar(value=SAMPLERATE_LIST[5])
        self._status = StringVar(value="")
        self._sound_list = list[Sound]()
        self._active_thread = list()
        self._on_exit = False
        self._on_pause = False

        """ MAIN MENU """
        menu = Menu(master)
        master.config(menu=menu)

        file_menu = Menu(menu, tearoff=0)
        help_menu = Menu(menu, tearoff=0)

        file_menu.add_command(label="Импорт файлов", command=self._open_files)
        file_menu.add_command(label="Экспорт", command=self._save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=master.destroy)

        help_menu.add_command(label="Помощь")
        help_menu.add_command(label="О программе")

        menu.add_cascade(label="Файл", menu=file_menu)
        menu.add_cascade(label="Справка", menu=help_menu)

        """ BASE FRAMES """
        toolbar = Frame(master, borderwidth=1, relief="ridge")
        sound_frame = ScrolledFrame(master, borderwidth=0, scrollbars="both")
        status_bar = Frame(master, borderwidth=1, relief="ridge")

        toolbar.pack(side="top", padx=2, pady=2, fill="x")
        sound_frame.pack(side="top", fill="both", expand=True)
        status_bar.pack(side="bottom", fill="x")

        """ TOOLBAR FRAMES """
        play_frame = Frame(toolbar)
        volume_frame = LabelFrame(toolbar, text="Громкость", labelanchor="n")
        samplerate_frame = LabelFrame(toolbar, text="Частота дискретизации", labelanchor="n")

        play_frame.pack(side="left", padx=2)
        volume_frame.pack(side="right", fill="y", padx=2)
        samplerate_frame.pack(side="right", fill="y", padx=2)

        """ PLAY FRAME """
        play_button = Button(play_frame, text="Играть", command=self._play_sound)
        pause_button = Button(play_frame, text="Пауза", command=self._pause_sound)
        stop_button = Button(play_frame, text="Стоп", command=sa.stop_all)
        record_button = Button(play_frame, text="Запись", command=self._record_sound)

        play_button.pack(side="left", fill="both", padx=2, pady=2)
        pause_button.pack(side="left", fill="both", padx=2, pady=2)
        stop_button.pack(side="left", fill="both", padx=2, pady=2)
        record_button.pack(side="left", fill="both", padx=2, pady=2)

        """ VOLUME FRAME"""
        volume_scale = Scale(volume_frame, orient="horizontal", length=100, from_=-50.0, to=0.0,
                             variable=self._volume,
                             command=lambda s: self._volume.set(value=round(float(s))))
        volume_scale.pack(padx=2, pady=2)
        volume_scale.bind("<Button-2>", func=lambda e: self._volume.set(value=0))
        volume_scale.bind("<Double-Button-1>", lambda e: change_value("Громкость", self._volume, -50, 0))
        ToolTip(volume_scale, msg=self._msg_volume(), delay=0)

        """ SAMPLERATE FRAME"""
        samplerate_combobox = Combobox(samplerate_frame, values=SAMPLERATE_LIST,
                                       textvariable=self._samplerate, state="readonly")
        samplerate_combobox.current(5)
        samplerate_combobox.pack(fill="both", padx=2, pady=2)

        """ SOUND FRAME """
        sound_frame.bind_arrow_keys(master)
        sound_frame.bind_scroll_wheel(master)
        self.sound_inner_frame = sound_frame.display_widget(Frame)

        """ STATUS BAR FRAME"""
        self._status_bar_label = Label(status_bar, textvariable=self._status)
        self._status_bar_label.pack(side="left")

        """ TRACKING FUNCTIONS START """
        thread_track_closed = threading.Thread(target=self._closed_tracking, args=())
        thread_track_closed.start()

        thread_track_solo = threading.Thread(target=self._solo_tracking, args=())
        thread_track_solo.start()

    def _closed_tracking(self):
        while not self._on_exit:
            for sound in self._sound_list:
                if sound.is_close():
                    self._sound_list.remove(sound)
                    del sound
                    self._regrid()
            sleep(0.1)

    def _solo_tracking(self):
        current = Sound.solo_id
        while not self._on_exit:
            if current != Sound.solo_id:
                current = Sound.solo_id
                for sound in self._sound_list:
                    sound.solo_tracking()
            sleep(0.1)

    def _wait_play(self, play_object: sa.PlayObject):
        Sound.delete_allowed = False
        play_object.wait_done()
        self._status.set("Остановленно")
        Sound.delete_allowed = True

    def _msg_volume(self):
        return "Громоксть воспроизведения: " + str(self._volume.get()) + " дБ"

    def _open_files(self):
        filepath = filedialog.askopenfilenames(title="Выберите один или несколько файлов", filetypes=EXTENSION_LIST)

        if filepath != "":
            for sound in filepath:
                self._sound_list.append(Sound(self.sound_inner_frame, sound))

            self._regrid()

    def _save_file(self):
        filepath = filedialog.asksaveasfilename(title="Экспорт аудиоданных", defaultextension=EXTENSION_LIST[1][1],
                                                initialfile="Song", filetypes=EXTENSION_LIST[1:])
        sound_list = [sound.get_sound() for sound in self._sound_list]
        if filepath != "":
            sound = overlay_sounds(sound_list, self._samplerate.get())
            sound.export(filepath, format=os.path.splitext(filepath)[1][1:])

    def _play_sound(self):
        if self._on_pause:
            self._on_pause = False
            self._status.set("Играет")

        else:
            sa.stop_all()
            sound_list = self._get_active_sound()

            if len(sound_list):
                sound = overlay_sounds(sound_list, self._samplerate.get()) + self._volume.get()
                play_object = sa.play_buffer(audio_data=sound.raw_data, num_channels=sound.channels,
                                             bytes_per_sample=sound.sample_width, sample_rate=sound.frame_rate)
                self._status.set("Играет")

                thread = threading.Thread(target=self._wait_play, args=(play_object,))
                thread.start()
                self._active_thread.append(thread)
            else:
                messagebox.showinfo(title="Воспроизведение невозможно", message="Нет аудио для воспроизведения")

    def _record_sound(self):
        self._status.set("Запись")

        self._status.set("")

    def _pause_sound(self):
        self._on_pause = True
        self._status.set("Пауза")

    def _get_active_sound(self):
        sound_list = list()
        for sound in self._sound_list:
            sound_list.append(sound.get_sound())
        return sound_list

    def _regrid(self):
        for i in range(0, len(self._sound_list)):
            self._sound_list[i].grid(i)

    def is_empty(self):
        return len(self._sound_list) == 0

    def close(self):
        self._on_exit = True
        sa.stop_all()


if __name__ == "__main__":
    def on_exit():
        if app.is_empty() or messagebox.askokcancel("Выход", "Вы действительно хотите выйти?"):
            app.close()
            root.destroy()

    root = Tk()
    root.iconbitmap(default="icon.ico")
    root.title("Аудио редактор")
    root.state('zoomed')
    root.protocol("WM_DELETE_WINDOW", on_exit)

    app = MainApp(root)
    root.mainloop()
