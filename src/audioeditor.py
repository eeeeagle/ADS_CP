import os.path
import simpleaudio as sa
import threading

from time import sleep
from pydub import AudioSegment
from tkinter import IntVar, StringVar, Menu, Misc, Toplevel, PhotoImage
from tkinter.ttk import Label, LabelFrame, Scale, Combobox, Progressbar, Frame, Button
from tkinter.messagebox import askokcancel, showinfo
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from tktooltip import ToolTip
from tkscrolledframe import ScrolledFrame

from sound import Sound
from valuewindow import change_value


class AudioEditor(Frame):
    STATUS_LIST = ["Остановленно", "Играет"]
    SAMPLERATE_LIST = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000, 352800, 384000]
    EXTENSION_LIST = [("Все поддерживаемые форматы", ".wav .flac .m4a .mp3 .ogg"),
                      ("Microsoft Wave", ".wav"),
                      ("Free Lossless Audio Codec", ".flac"),
                      ("Apple Lossless", ".m4a"),
                      ("MPEG Layer 3", ".mp3"),
                      ("Ogg Vorbis Audio", ".ogg")]

    def __init__(self, master: Misc = None,):
        super().__init__(master)

        """ MASTER """
        self.master.iconbitmap(default="icon/app.ico")
        self.master.title("Аудио редактор")
        self.master.state('zoomed')
        self.master.protocol("WM_DELETE_WINDOW", self.close)

        """ VARIABLES """
        self._volume = IntVar(value=0)
        self._samplerate = IntVar(value=self.SAMPLERATE_LIST[5])
        self._status = StringVar(value=self.STATUS_LIST[0])
        self._sound_list = list[Sound]()
        self._on_exit = False

        """ MAIN MENU """
        menu = Menu(master)
        self.master.config(menu=menu)

        menu.add_cascade(label="Импорт файлов", command=self._open_files)
        menu.add_cascade(label="Экспорт", command=self._save_file)

        """ BASE FRAMES """
        toolbar = Frame(self.master)
        sound_frame = ScrolledFrame(self.master, borderwidth=0, scrollbars="both")
        status_bar = Frame(self.master)

        toolbar.pack(side="top", padx=2, pady=2, fill="x")
        sound_frame.pack(side="top", fill="both", expand=True)
        status_bar.pack(side="bottom", fill="x")

        """ TOOLBAR FRAMES """
        play_frame = Frame(toolbar)
        samplerate_frame = LabelFrame(toolbar, text="Частота дискретизации", labelanchor="n")
        volume_frame = LabelFrame(toolbar, text="Громкость", labelanchor="n")

        play_frame.pack(side="left", padx=2)
        samplerate_frame.pack(side="right", fill="y", padx=2)
        volume_frame.pack(side="right", fill="y", padx=2)

        """ PLAY FRAME """
        self.PLAY_IMAGE = PhotoImage(file="icon/play.png")
        self.STOP_IMAGE = PhotoImage(file="icon/stop.png")

        play_button = Button(play_frame, image=self.PLAY_IMAGE, command=self._play_sound)
        stop_button = Button(play_frame, image=self.STOP_IMAGE, command=sa.stop_all)

        play_button.pack(side="left", padx=2, pady=2)
        stop_button.pack(side="left", padx=2, pady=2)

        """ VOLUME FRAME"""
        volume_scale = Scale(volume_frame, orient="horizontal", length=100, from_=-50, to=0,
                             variable=self._volume,
                             command=lambda s: self._volume.set(value=round(float(s))))
        volume_scale.pack(padx=2, pady=2)
        volume_scale.bind("<Button-2>", func=lambda e: self._volume.set(value=0))
        volume_scale.bind("<Double-Button-1>", lambda e: change_value("Громкость", self._volume, -50, 0))
        ToolTip(volume_scale, msg=self._msg_volume, delay=0, x_offset=-50)

        """ SAMPLERATE FRAME"""
        samplerate_combobox = Combobox(samplerate_frame, values=self.SAMPLERATE_LIST,
                                       textvariable=self._samplerate, state="readonly")
        samplerate_combobox.current(5)
        samplerate_combobox.pack(fill="both", padx=2, pady=2)

        """ SOUND FRAME """
        sound_frame.bind_scroll_wheel(self.master)
        self.sound_inner_frame = sound_frame.display_widget(Frame)

        """ STATUS BAR FRAME"""
        status_bar_label = Label(status_bar, textvariable=self._status)
        status_bar_label.pack(side="left")

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
        self._status.set(self.STATUS_LIST[0])
        Sound.delete_allowed = True

    def _msg_volume(self):
        return "Громоксть воспроизведения: " + str(self._volume.get()) + " дБ"

    @staticmethod
    def overlay_sounds(sound_list: list[AudioSegment], samplerate: int):
        output_sound = AudioSegment.silent(duration=max([len(sound) for sound in sound_list]), frame_rate=samplerate)
        for sound in sound_list:
            output_sound = output_sound.overlay(sound)
        output_sound = output_sound.set_frame_rate(samplerate)
        return output_sound

    def _open_files(self):
        filepath = askopenfilenames(title="Выберите один или несколько файлов", filetypes=self.EXTENSION_LIST)

        if filepath != "":
            def progress():
                window = Toplevel()
                window.wm_attributes('-disabled', True)
                window.wm_attributes('-toolwindow', True)
                window.title("Чтение")
                window.geometry("250x100")
                window.resizable(False, False)
                window.grab_set()

                label = Label(window, text="Идёт загрузка", anchor="n", justify="center")
                progressbar = Progressbar(window, mode="determinate", variable=common_value, maximum=len(filepath))

                label.pack(side="top", fill="both", padx=2, pady=2)
                progressbar.pack(side="top", fill="both", padx=2, pady=2)

                while flag:
                    window.update()
                    window.update_idletasks()

                label['text'] = "Загруженно"
                sleep(1)

                window.grab_release()
                window.destroy()

            common_value = IntVar(value=0)
            thread = threading.Thread(target=progress, args=())
            thread.start()

            flag = True
            for sound in filepath:
                self._sound_list.append(Sound(self.sound_inner_frame, sound))
                self.sound_inner_frame.update()
                common_value.set(common_value.get() + 1)
            self._regrid()
            flag = False

    def _save_file(self):
        filepath = asksaveasfilename(title="Экспорт аудиоданных", defaultextension=self.EXTENSION_LIST[1][1],
                                     initialfile="Song", filetypes=self.EXTENSION_LIST[1:])
        sound_list = [sound.get_sound() for sound in self._sound_list]
        if filepath != "":
            sound = self.overlay_sounds(sound_list, self._samplerate.get())
            sound.export(filepath, format=os.path.splitext(filepath)[1][1:])

    def _play_sound(self):
        sa.stop_all()
        sound_list = self._get_active_sound()

        if len(sound_list):
            sound = self.overlay_sounds(sound_list, self._samplerate.get()) + self._volume.get()
            play_object = sa.play_buffer(audio_data=sound.raw_data, num_channels=sound.channels,
                                         bytes_per_sample=sound.sample_width, sample_rate=sound.frame_rate)
            self._status.set(self.STATUS_LIST[1])

            thread = threading.Thread(target=self._wait_play, args=(play_object,))
            thread.start()
        else:
            showinfo(title="Воспроизведение невозможно", message="Нет аудио для воспроизведения")

    def _get_active_sound(self):
        sound_list = list[AudioSegment]()
        for sound in self._sound_list:
            sound_list.append(sound.get_sound())
        return sound_list

    def _regrid(self):
        for i in range(0, len(self._sound_list)):
            self._sound_list[i].grid(i)

    def close(self):
        if len(self._sound_list) == 0 or askokcancel("Выход", "Вы действительно хотите выйти?"):
            self.master.destroy()
            sa.stop_all()
            self._on_exit = True

    def destroy(self):
        return super().destroy()


if __name__ == "__main__":
    app = AudioEditor()
    app.mainloop()
