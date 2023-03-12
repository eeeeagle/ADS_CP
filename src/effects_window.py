from tkinter.ttk import Checkbutton, Button, Frame, Label, LabelFrame, Scale
from tkinter import Toplevel, Listbox, BooleanVar, IntVar, DoubleVar, Misc, StringVar
from pydub import AudioSegment, effects
from pydub.playback import play
from value_window import change_value


EFFECTS_LIST: list[str] = ["Нормализация",
                           "Изменение скорости",
                           "Компрессор",
                           "Инвертирование фазы",
                           "Фильтр низких частот",
                           "Фильтр высоких частот",
                           "Инвертирование дорожки",
                           "Усиление",
                           "Фейд-подъём",
                           "Фейд-спад",
                           "Обрезка тишины"]


class Setting(LabelFrame):
    def __init__(self,
                 master: Misc,
                 label_text: str,
                 scale_from: int | float,
                 scale_to: int | float,
                 default_value: int | float):

        super().__init__(master, borderwidth=1, relief="solid", text=label_text, labelanchor="n")

        if type(default_value) is int:
            self._value = IntVar(value=default_value)
        if type(default_value) is float:
            self._value = DoubleVar(value=default_value)

        value_label = Label(self, textvariable=self._value, justify="center")
        scale = Scale(self, orient="horizontal", from_=scale_from, to=scale_to,
                      variable=self._value, command=lambda e: self.set_value(e))
        scale.bind("<Double-Button-1>", lambda e: change_value(label_text, self._value, scale_from, scale_to))
        scale.bind("<Button-2>", func=lambda e: self._value.set(value=default_value))

        value_label.pack(side="top", padx=2, pady=2)
        scale.pack(side="top", fill="both", padx=2, pady=2)

    def set_value(self, event):
        if self._value is DoubleVar:
            self._value.set(round(float(event), 2))
        else:
            self._value.set(round(float(event)))

    def get_value(self):
        return self._value.get()


class EffectFrame(Frame):
    def __init__(self, master: Misc = None,):
        super().__init__(master)

    def set_effect(self, segment: AudioSegment):
        return segment


class Normalize(EffectFrame):
    def __init__(self, master: Misc = None,):
        super().__init__(master)

        self.headroom = Setting(self, "Нормализовать пик амплитуды (дБ)",
                                scale_from=-145.0, scale_to=0.0, default_value=-1.0)
        self.headroom.pack(side="top", fill="both")

    def set_effect(self, segment: AudioSegment):
        return effects.normalize(segment,
                                 headroom=self.headroom.get_value())


class SpeedChange(EffectFrame):
    def __init__(self, master: Misc = None,):
        super().__init__(master)

        self.playback_speed = Setting(self, "Коэффициент ускорения", scale_from=0.01, scale_to=5.0, default_value=1.0)
        self.playback_speed.pack(side="top", fill="both")

    def set_effect(self, segment: AudioSegment):
        return effects.speedup(segment,
                               playback_speed=self.playback_speed.get_value())


class Compressor(EffectFrame):
    def __init__(self, master: Misc = None,):
        super().__init__(master)

        self.threshold = Setting(self, "Порог (дБ)", scale_from=-60, scale_to=-1, default_value=-20)
        self.ratio = Setting(self, "Пропорции (value : 1)", scale_from=1.1, scale_to=10, default_value=2)
        self.attack = Setting(self, "Время атаки (мс)", scale_from=100, scale_to=5000, default_value=200)
        self.release = Setting(self, "Время затухания (мс)", scale_from=1000, scale_to=30000, default_value=1000)

        self.threshold.pack(side="top", fill="both", padx=2, pady=2)
        self.ratio.pack(side="top", fill="both", padx=2, pady=2)
        self.attack.pack(side="top", fill="both", padx=2, pady=2)
        self.release.pack(side="top", fill="both", padx=2, pady=2)

    def set_effect(self, segment: AudioSegment):
        return effects.compress_dynamic_range(segment,
                                              threshold=self.threshold.get_value(),
                                              ratio=self.ratio.get_value(),
                                              attack=self.attack.get_value(),
                                              release=self.release.get_value())


class PhaseInvert(EffectFrame):
    def __init__(self, master: Misc = None,):
        super().__init__(master)

        label = Label(self, text="Нет дополнительных настроек", justify="center")
        label.pack(side="top", fill="both", padx=2, pady=2)

    def set_effect(self, segment: AudioSegment):
        return effects.invert_phase(segment).split_to_mono()[0]


class LowPassFilter(EffectFrame):
    def __init__(self, master: Misc = None,):
        super().__init__(master)

        self.cutoff = Setting(self, "Частота (Гц)", scale_from=1, scale_to=1000, default_value=100)
        self.cutoff.pack(side="top", fill="both", padx=2, pady=2)

    def set_effect(self, segment: AudioSegment):
        return effects.low_pass_filter(segment, cutoff=self.cutoff.get_value())


class HighPassFilter(EffectFrame):
    def __init__(self, master: Misc = None,):
        super().__init__(master)

        self.cutoff = Setting(self, "Частота (Гц)", scale_from=200, scale_to=24000, default_value=1000)
        self.cutoff.pack(side="top", fill="both", padx=2, pady=2)

    def set_effect(self, segment: AudioSegment):
        return effects.high_pass_filter(segment, cutoff=self.cutoff.get_value())


class Reverse(EffectFrame):
    def __init__(self, master: Misc = None,):
        super().__init__(master)

        label = Label(self, text="Нет дополнительных настроек", justify="center")
        label.pack(side="top", fill="both", padx=2, pady=2)

    def set_effect(self, segment: AudioSegment):
        return segment.reverse()


class Pan(EffectFrame):
    def __init__(self, master: Misc = None,):
        super().__init__(master)

        self.pan = Setting(self, "Баланс (лево/право)", scale_from=-100, scale_to=100, default_value=0)
        self.pan.pack(side="top", fill="both", padx=2, pady=2)

    def set_effect(self, segment: AudioSegment):
        return effects.pan(segment, pan_amount=self.pan.get_value() / 100)


class Gain(EffectFrame):
    def __init__(self, master: Misc = None,):
        super().__init__(master)

        self.gain = Setting(self, "Усиление (дБ)", scale_from=-50.0, scale_to=50.0, default_value=0)
        self.gain.pack(side="top", fill="both", padx=2, pady=2)

    def set_effect(self, segment: AudioSegment):
        return segment + self.gain.get_value()


class FadeIn(EffectFrame):
    def __init__(self, master: Misc = None,):
        super().__init__(master)

        label = Label(self, text="Нет дополнительных настроек", justify="center")
        label.pack(side="top", fill="both", padx=2, pady=2)

    def set_effect(self, segment: AudioSegment):
        return segment.fade_in(len(segment))


class FadeOut(EffectFrame):
    def __init__(self, master: Misc = None,):
        super().__init__(master)

        label = Label(self, text="Нет дополнительных настроек", justify="center")
        label.pack(side="top", fill="both", padx=2, pady=2)

    def set_effect(self, segment: AudioSegment):
        return segment.fade_out(len(segment))


class SilenceStrip(EffectFrame):
    def __init__(self, master: Misc = None,):
        super().__init__(master)

        self.threshold = Setting(self, "Порог (дБ)", scale_from=-100, scale_to=-1, default_value=-20)
        self.duration = Setting(self, "Длительность (мс)", scale_from=101, scale_to=20000, default_value=1000)

        self.threshold.pack(side="top", fill="both", padx=2, pady=2)
        self.duration.pack(side="top", fill="both", padx=2, pady=2)

    def set_effect(self, segment: AudioSegment):
        return effects.strip_silence(segment, silence_len=self.duration, silence_thresh=self.threshold)


def apply_effect(segment: AudioSegment):
    # VARIABLES
    is_working = True
    edited = False
    enabled_list = list()
    effect = StringVar(value=EFFECTS_LIST)

    # FUNCTIONS
    def close_window():
        nonlocal is_working
        is_working = False

        window.grab_release()
        window.destroy()

    def effect_select():
        nonlocal edited, effect_settings

        try:
            selected_index = listbox.curselection()[0]
        except IndexError:
            return

        if selected_index == 0:
            effect_settings = Normalize(settings_frame)
        if selected_index == 1:
            effect_settings = SpeedChange(settings_frame)
        if selected_index == 2:
            effect_settings = Compressor(settings_frame)
        if selected_index == 3:
            effect_settings = PhaseInvert(settings_frame)
        if selected_index == 4:
            effect_settings = LowPassFilter(settings_frame)
        if selected_index == 5:
            effect_settings = HighPassFilter(settings_frame)
        if selected_index == 6:
            effect_settings = Reverse(settings_frame)
        if selected_index == 7:
            effect_settings = Gain(settings_frame)
        if selected_index == 8:
            effect_settings = FadeIn(settings_frame)
        if selected_index == 9:
            effect_settings = FadeOut(settings_frame)
        if selected_index == 10:
            effect_settings = SilenceStrip(settings_frame)

        effect_settings.grid(row=0, column=0, columnspan=3, padx=2, pady=2, sticky="nsew")

    def apply():
        nonlocal edited, segment

        mono_segments = segment.split_to_mono()
        for j in range(0, segment.channels):
            if enabled_list[j].get():
                mono_segments[j] = effect_settings.set_effect(mono_segments[j])

        segment = AudioSegment.from_mono_audiosegments(*mono_segments)
        edited = True
        close_window()

    def try_play():  # Play 5 first seconds
        mono_segments = segment.split_to_mono()
        for j in range(0, segment.channels):
            if enabled_list[j].get():
                mono_segments[j] = effect_settings.set_effect(mono_segments[j])
        audio = AudioSegment.from_mono_audiosegments(*mono_segments)[:5000]
        play(audio)

    # WINDOW
    window = Toplevel()
    window.wm_attributes('-toolwindow', 'True')
    window.title("Эффекты")
    window.geometry("640x390")
    window.resizable(False, False)
    window.protocol("WM_DELETE_WINDOW", close_window)

    # CHILD FRAMES
    channel_frame = Frame(window)
    effects_frame = Frame(window)
    settings_frame = Frame(window)

    # CHILD FRAMES PACK
    channel_frame.pack(side="left", fill="both", padx=2, pady=2)
    effects_frame.pack(side="left", fill="both", padx=2, pady=2)
    settings_frame.pack(side="left", fill="both", padx=2, pady=2)

    # CHANNEL FRAME
    for i in range(segment.channels):
        enabled_list.append(BooleanVar(value=True))
        Checkbutton(channel_frame, text="Канал " + str(i + 1), variable=enabled_list[-1]).pack(side="top", fill="both")

    # LISTBOX FRAME
    listbox = Listbox(effects_frame, listvariable=effect, selectmode="single", width=50)
    listbox.pack(side="top", fill="both", expand=True, padx=2, pady=2)
    listbox.bind("<<ListboxSelect>>", lambda e: effect_select())

    # SETTINGS FRAME
    effect_settings = EffectFrame(settings_frame)
    play_button = Button(settings_frame, text="Прослушать", command=try_play)
    apply_button = Button(settings_frame, text="Применить", command=apply)
    cancel_button = Button(settings_frame, text="Отменить", command=close_window)

    effect_settings.grid(row=0, column=0, columnspan=3, padx=2, pady=2, sticky="nsew")
    play_button.grid(row=1, column=0, padx=2, pady=2)
    apply_button.grid(row=1, column=1, padx=2, pady=2)
    cancel_button.grid(row=1, column=2, padx=2, pady=2)

    settings_frame.grid_rowconfigure(0, weight=1)
    settings_frame.grid_rowconfigure(1, weight=0)

    settings_frame.grid_columnconfigure(0, weight=1)
    settings_frame.grid_columnconfigure(1, weight=1)
    settings_frame.grid_columnconfigure(2, weight=1)

    window.grab_set()

    while is_working:
        window.update_idletasks()
        window.update()

    return segment, edited
