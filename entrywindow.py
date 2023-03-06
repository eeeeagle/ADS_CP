from tkinter.ttk import Entry
from tkinter import Button, Toplevel, Frame
from tkinter.messagebox import showerror
from time import sleep


class EntryWindow:
    def __init__(self, window_name: str, current: int | float, from_: int | float, to: int | float):
        self.from_ = from_
        self.to = to
        self.value = current

        self.window = Toplevel()
        self.window.wm_attributes('-toolwindow', 'True')
        self.window.title(window_name)
        self.window.geometry("150x150")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

        self.root = Frame(self.window)
        self.root.pack(side="top", expand=True)

        self.entry = Entry(self.root)
        self.ok_button = Button(self.root, text="ОК", command=self._validate)
        self.cancel_button = Button(self.root, text="Отмена", command=self._close_window)

        self.entry.grid(row=0, column=0, columnspan=2, padx=2, pady=2, sticky="we")
        self.ok_button.grid(row=1, column=0, padx=2, pady=2, sticky="we")
        self.cancel_button.grid(row=1, column=1, padx=2, pady=2, sticky="we")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

        self.window.grab_set()
        self.running = True
        while self.running:
            while True:
                sleep(0.1)
                break

    def _close_window(self):
        self.window.grab_release()
        self.running = False
        self.window.destroy()

    def _validate(self):
        try:
            new_val = float(self.entry.get())
        except ValueError:
            showerror(title="Ошибка проверки",
                      message="Поле для ввода содержит постороние элементы")
            return

        if self.from_ <= new_val <= self.to:
            self.value = new_val
            self._close_window()
        else:
            showerror(title="Ошибка проверки",
                      message="Число не в диапозоне от " + str(self.from_) + " до " + str(self.to))
