from tkinter import Button, Toplevel, Variable
from tkinter.ttk import Entry
from tkinter.messagebox import showerror


def change_value(title: str, variable: Variable, from_: int | float, to: int | float):
    is_working = True

    def close_window():
        nonlocal is_working
        window.grab_release()
        window.destroy()
        is_working = False

    def validate():
        nonlocal value
        try:
            new_value = type(value)(entry.get())
        except ValueError:
            showerror(title="Ошибка проверки", message="Поле для ввода содержит постороние элементы")
            return

        if from_ <= new_value <= to:
            value = new_value
            close_window()
        else:
            showerror(title="Ошибка проверки", message="Число не в диапозоне от " + str(from_) + " до " + str(to))

    value = variable.get()

    window = Toplevel()
    window.wm_attributes('-toolwindow', 'True')
    window.title(title)
    window.geometry("250x250")
    window.resizable(False, False)
    window.protocol("WM_DELETE_WINDOW", close_window)

    entry = Entry(window)
    ok_button = Button(window, text="ОК", command=validate)
    cancel_button = Button(window, text="Отмена", command=close_window)

    entry.grid(row=0, column=0, columnspan=2, padx=2, pady=2, sticky="we")
    ok_button.grid(row=1, column=0, padx=2, pady=2, sticky="we")
    cancel_button.grid(row=1, column=1, padx=2, pady=2, sticky="we")

    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=1)

    window.grab_set()

    while is_working:
        window.update_idletasks()
        window.update()

    variable.set(value)
