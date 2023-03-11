from tkinter.ttk import Checkbutton
from tkinter import Button, Toplevel, Frame, Listbox, BooleanVar, Variable, DoubleVar, Label, Scale
from pydub import AudioSegment, effects
from pydub.playback import play


EFFECTS_LIST = ["Нормализация",
                "Ускорение",
                "Компрессор",
                "Инвертирование фазы",
                "Фильтр низких частот",
                "Фильтр высоких частот",
                "Инвертирование дорожки"]


def apply_normalize(segment: AudioSegment, selected_list: list[bool]):
    is_working = True
    edited = False

    def close_window():
        nonlocal is_working
        is_working = False
        window.grab_release()
        window.destroy()

    def apply():
        nonlocal edited
        for i in range(0, channels):
            if selected_list[i]:
                mono_segments[i] = effects.normalize(mono_segments[i], headroom=value.get())
        edited = True
        close_window()

    def try_play():
        for i in range(0, channels):
            if selected_list[i]:
                mono_segments[i] = effects.normalize(mono_segments[i], headroom=value.get())
        audio = AudioSegment.from_mono_audiosegments(*mono_segments)[:5000]  # Play 5 first seconds
        play(audio)

    mono_segments = segment.split_to_mono()
    channels = segment.channels
    value = DoubleVar(value=0.0)

    window = Toplevel()
    window.wm_attributes('-toolwindow', 'True')
    window.title("Нормализация")
    window.geometry("300x200")
    window.resizable(False, False)
    window.protocol("WM_DELETE_WINDOW", close_window)

    label = Label(window, text="Нормализовать пик амплитуды (максимум 0.0 дБ)")
    label_var = Label(window, textvariable=value)
    value_scale = Scale(window, orient="horizontal", from_=-145, to=0, variable=value,
                        command=lambda e: value.set(round(float(e), 0)))
    play_button = Button(window, text="Прослушать", justify="center", command=try_play)
    apply_button = Button(window, text="Применить", justify="center", command=apply)
    cancel_button = Button(window, text="Отменить", justify="center", command=close_window)

    label.grid(row=0, column=0, columnspan=3)
    label_var.grid(row=1, column=0, columnspan=3)
    value_scale.grid(row=2, column=0, columnspan=3)
    play_button.grid(row=3, column=0)
    apply_button.grid(row=3, column=1)
    cancel_button.grid(row=3, column=2)

    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=1)

    window.grab_set()

    while is_working:
        window.update_idletasks()
        window.update()

    return segment, edited


def apply_effect(segment: AudioSegment):
    is_working = True

    def close_window():
        nonlocal is_working
        is_working = False
        window.grab_release()
        window.destroy()

    def effect_select():
        selected_index = listbox.curselection()[0]
        selected_channels = [channel.get() for channel in enabled_list]
        window.grab_release()
        if selected_index == 0:
            apply_normalize(segment, selected_channels)
        window.grab_set()

    enabled_list = list()
    effect = Variable(value=EFFECTS_LIST)

    window = Toplevel()
    window.wm_attributes('-toolwindow', 'True')
    window.title("Эффекты")
    window.geometry("300x200")
    window.resizable(False, False)
    window.protocol("WM_DELETE_WINDOW", close_window)

    channel_frame = Frame(window)
    effects_frame = Frame(window)

    channel_frame.pack(side="left", fill="both", padx=2, pady=2)
    effects_frame.pack(side="right", fill="both", padx=2, pady=2)

    for i in range(segment.channels):
        enabled_list.append(BooleanVar(value=True))
        Checkbutton(channel_frame, text="Канал " + str(i + 1), variable=enabled_list[-1]).pack(side="top", fill="both")

    listbox = Listbox(effects_frame, listvariable=effect, selectmode="single", width=50)
    listbox.pack(side="top", fill="both", expand=True, padx=2, pady=2)
    listbox.bind("<Double-1>", lambda e: effect_select())

    window.grab_set()

    while is_working:
        window.update_idletasks()
        window.update()

    return segment
