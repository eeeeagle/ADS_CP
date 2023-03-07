import threading
from tkinter.ttk import Entry
from tkinter import Button, Toplevel, Frame, Variable
from tkinter.messagebox import showerror
from time import sleep


class EntryWindow:
    def __init__(self, title: str, current: int | float, from_: int | float, to: int | float):
        self._FROM = from_
        self._TO = to
        self._value = current

        self._window = Toplevel()
        self._window.wm_attributes('-toolwindow', 'True')
        self._window.title(title)
        self._window.geometry("150x150")
        self._window.resizable(False, False)
        self._window.protocol("WM_DELETE_WINDOW", self._close_window)

        root = Frame(self._window)
        self._entry = Entry(root)
        ok_button = Button(root, text="ОК", command=self._validate)
        cancel_button = Button(root, text="Отмена", command=self._close_window)

        root.pack(side="top", expand=True)

        self._entry.grid(row=0, column=0, columnspan=2, padx=2, pady=2, sticky="we")
        ok_button.grid(row=1, column=0, padx=2, pady=2, sticky="we")
        cancel_button.grid(row=1, column=1, padx=2, pady=2, sticky="we")

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)

        self._window.grab_set()

        self._running = True
        while self._running:
            sleep(0.1)

    def _close_window(self):
        self._window.grab_release()
        self._running = False
        self._window.destroy()

    def _validate(self):
        try:
            new_val = type(self._value)(self._entry.get())
        except ValueError:
            showerror(title="Ошибка проверки", message="Поле для ввода содержит постороние элементы")
            return

        if self._FROM <= new_val <= self._TO:
            self._value = new_val
            self._close_window()
        else:
            showerror(title="Ошибка проверки",
                      message="Число не в диапозоне от " + str(self._FROM) + " до " + str(self._TO))

    def get_value(self):
        return self._value


def change_value(title: str, variable: Variable, from_: int | float, to: int | float):
    def extra_window():
        nonlocal variable
        window = EntryWindow(title, variable.get(), from_, to)
        variable.set(value=window.get_value())

    thr = threading.Thread(target=extra_window, args=())
    thr.start()
