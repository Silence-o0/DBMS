import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from dbclasses import *


def interface():
    root = tk.Tk()
    root.title("DBMS")
    database = None

    def create_database():
        nonlocal database
        db_name = simpledialog.askstring("Нова база даних", "Введіть назву нової бази даних:")
        if db_name:
            database = Database(db_name)
            open_main_window()

    def load_database():
        nonlocal database
        file_path = filedialog.askopenfilename(title="Оберіть файл бази даних",
                                               filetypes=(("Database Files", "*.json"), ("All Files", "*.*")))
        try:
            if file_path:
                database = Database("Uploaded database", file=str(file_path))
                open_main_window()
        except Exception as e:
            messagebox.showinfo("Помилка", f"Неможливо відкрити файл. {str(e)}")

    def open_main_window():
        root.withdraw()
        main_window = tk.Toplevel()
        main_window.title("DBMS | " + database.name)
        current_table = None

        def load_table_data(*args):
            nonlocal current_table
            table_name = table_selector.get()
            current_table = database.tables.get(table_name)
            data_table.delete(*data_table.get_children())

            if not current_table:
                return

            columns = list(current_table.columns.keys())
            data_table["columns"] = columns
            for col in columns:
                data_table.heading(col, text=col)
                data_table.column(col, width=100)

            for row_id, row in current_table.rows.items():
                values = [row.values.get(col) if row.values.get(col) is not None else "" for col in columns]
                data_table.insert("", "end", values=values)

        def add_new_table():
            new_table_name = simpledialog.askstring("Нова таблиця", "Введіть назву нової таблиці:")
            if new_table_name:
                bool_result = database.create_table(new_table_name)
                if bool_result:
                    table_selector.set(new_table_name)
                    menu.add_command(label=new_table_name, command=lambda: table_selector.set(new_table_name))
                    load_table_data()
                else:
                    messagebox.showinfo("Помилка", f"Таблиця з такою назвою вже існує")

        def add_row():
            if current_table:
                row_window = tk.Toplevel()
                row_window.title("Додати новий рядок")
                entries = {}

                for col_name, col_type in current_table.columns.items():
                    frame = tk.Frame(row_window)
                    frame.pack(fill=tk.X, padx=5, pady=5)

                    if col_type == Type.time:
                        label_text = f"{col_name} | формат: HH:MM:SS"
                    elif col_type == Type.timeInvl:
                        label_text = f"{col_name} | формат: HH:MM:SS - HH:MM:SS"
                    else:
                        label_text = f"{col_name} | тип: {col_type.value}"

                    label = tk.Label(frame, text=label_text, width=35)
                    label.pack(side=tk.LEFT)

                    if col_type == Type.timeInvl:
                        entry1 = tk.Entry(frame, width=8)
                        entry2 = tk.Entry(frame, width=8)
                        entry1.pack(side=tk.LEFT, padx=2)
                        tk.Label(frame, text="-").pack(side=tk.LEFT)
                        entry2.pack(side=tk.LEFT, padx=2)
                        entries[col_name] = (entry1, entry2)
                    else:
                        entry = tk.Entry(frame)
                        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                        entries[col_name] = entry

                def save_row():
                    new_row_data = {}
                    for col_name, widget in entries.items():
                        if isinstance(widget, tuple):
                            entry1, entry2 = widget
                            value = f"{entry1.get()}-{entry2.get()}"
                        else:
                            value = widget.get()
                        new_row_data[col_name] = value if value else None
                    try:
                        current_table.add_row(new_row_data)
                        row_window.destroy()
                        load_table_data()
                    except ValidError as e:
                        messagebox.showerror("Помилка", str(e))
                    except ValueError as e:
                        messagebox.showerror("Помилка", str(e))

                tk.Button(row_window, text="Зберегти", command=save_row).pack(pady=10)
                row_window.grab_set()
                row_window.wait_window()
            else:
                messagebox.showerror("Помилка", "Таблиця не обрана.")

        def add_column():
            if current_table:
                new_column_name = simpledialog.askstring("Додати колонку", "Введіть назву нової колонки:")
                if new_column_name:
                    type_window = tk.Toplevel()
                    type_window.title("Обрати тип даних")

                    tk.Label(type_window, text="Оберіть тип даних:").pack(pady=10)

                    type_var = tk.StringVar(value="string")
                    type_selector = ttk.OptionMenu(type_window, type_var, type_var.get(), *[t.value for t in Type])
                    type_selector.pack(pady=10)

                    def confirm_type():
                        selected_type = Type(type_var.get())
                        bool_result = current_table.add_column(new_column_name, selected_type)
                        if bool_result:
                            load_table_data()
                            type_window.destroy()
                        else:
                            messagebox.showerror("Помилка", "Не вдалося додати рядок.")

                    tk.Button(type_window, text="Обрати тип", command=confirm_type).pack(pady=10)
                    type_window.grab_set()
                    type_window.wait_window()
            else:
                messagebox.showerror("Помилка", "Таблиця не обрана.")

        def edit_row():
            selected_item = data_table.selection()[0]
            row_values = data_table.item(selected_item)["values"]

            for index, (column_name, val) in enumerate(zip(current_table.columns.keys(), row_values)):
                if not val:
                    row_values[index] = None
                else:
                    column_type = current_table.columns[column_name]
                    if column_type == Type.integer:
                        row_values[index] = int(val)
                    elif column_type == Type.real:
                        row_values[index] = float(val)

            row_id = None
            for rid, row in current_table.rows.items():
                if all(row.values.get(col) == value for col, value in zip(current_table.columns.keys(), row_values)):
                    row_id = rid
                    break
            if row_id is None:
                messagebox.showerror("Помилка", "Не вдалося знайти відповідний рядок. Спробуйте ще раз.")
                return

            current_row = current_table.rows[row_id]

            edit_window = tk.Toplevel()
            edit_window.title("Редагувати рядок")

            entries = {}

            for col_name, col_type in current_table.columns.items():
                frame = tk.Frame(edit_window)
                frame.pack(fill=tk.X, padx=5, pady=5)

                label_text = f"{col_name} | {col_type.value}" if col_type != Type.timeInvl else f"{col_name} | формат: HH:MM:SS - HH:MM:SS"
                label = tk.Label(frame, text=label_text, width=35)
                label.pack(side=tk.LEFT)

                current_value = current_row.values.get(col_name, "")
                if current_value is None:
                    current_value = ''

                if col_type == Type.timeInvl:
                    entry1 = tk.Entry(frame, width=8)
                    entry2 = tk.Entry(frame, width=8)
                    if current_value and '-' in current_value:
                        start, end = current_value.split('-')
                        entry1.insert(0, start.strip())
                        entry2.insert(0, end.strip())
                    entry1.pack(side=tk.LEFT, padx=2)
                    tk.Label(frame, text="-").pack(side=tk.LEFT)
                    entry2.pack(side=tk.LEFT, padx=2)
                    entries[col_name] = (entry1, entry2)
                else:
                    entry = tk.Entry(frame)
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    entry.insert(0, str(current_value))
                    entries[col_name] = entry

            def save_changes():
                new_values = {}
                for col_name, widget in entries.items():
                    if isinstance(widget, tuple):
                        entry1, entry2 = widget
                        value = f"{entry1.get()}-{entry2.get()}"
                    else:
                        value = widget.get()
                    new_values[col_name] = value if value else None

                try:
                    current_row.edit_row(new_values)
                    load_table_data()
                    edit_window.destroy()
                except ValidError as e:
                    messagebox.showerror("Помилка", str(e))
                except ValueError as e:
                    messagebox.showerror("Помилка", str(e))

            tk.Button(edit_window, text="Зберегти", command=save_changes).pack(pady=10)
            edit_window.grab_set()
            edit_window.wait_window()

        def compare_tables():
            compare_window = tk.Toplevel(main_window)
            compare_window.title("Порівняння таблиць")

            tk.Label(compare_window, text="Оберіть першу таблицю:").pack(pady=5)
            first_table = tk.StringVar(value="Обрати таблицю")
            first_dropdown = ttk.OptionMenu(compare_window, first_table, first_table.get(), *database.tables.keys())
            first_dropdown.pack(pady=5)

            tk.Label(compare_window, text="Оберіть другу таблицю:").pack(pady=5)
            second_table = tk.StringVar(value="Обрати таблицю")
            second_dropdown = ttk.OptionMenu(compare_window, second_table, second_table.get(), *database.tables.keys())
            second_dropdown.pack(pady=5)

            def get_difference():
                table1 = database.tables.get(first_table.get())
                table2 = database.tables.get(second_table.get())
                if not table1 or not table2:
                    messagebox.showerror("Помилка", "Оберіть дві таблиці для порівняння")
                    return

                try:
                    difference = table1.table_difference(table2)
                    result_window = tk.Toplevel(compare_window)
                    result_window.title("Результат порівняння")

                    result_frame = tk.Frame(result_window)
                    result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                    result_table = ttk.Treeview(result_frame, columns=list(table1.columns.keys()), show="headings")

                    for col in table1.columns.keys():
                        result_table.heading(col, text=col)
                        result_table.column(col, width=100)

                    for diff_row in difference:
                        values = [diff_row.values.get(col) if diff_row.values.get(col) is not None else "" for col in table1.columns.keys()]
                        result_table.insert("", "end", values=values)
                    result_table.pack(fill=tk.BOTH, expand=True)
                except ValueError as e:
                    messagebox.showerror("Помилка", str(e))
            tk.Button(compare_window, text="Отримати різницю", command=get_difference).pack(pady=10)

        def delete_row():
            selected_item = data_table.selection()[0]
            row_values = data_table.item(selected_item)["values"]
            for index, (column_name, val) in enumerate(zip(current_table.columns.keys(), row_values)):
                if not val:
                    row_values[index] = None
                else:
                    column_type = current_table.columns[column_name]
                    if column_type == Type.integer:
                        row_values[index] = int(val)
                    elif column_type == Type.real:
                        row_values[index] = float(val)

            row_id = None
            for rid, row in current_table.rows.items():
                if all(row.values.get(col) == value for col, value in zip(current_table.columns.keys(), row_values)):
                    row_id = rid
                    break
            if row_id is None:
                messagebox.showerror("Помилка", "Не вдалося знайти відповідний рядок. Спробуйте ще раз.")
                return

            if messagebox.askyesno("Підтвердження", "Ви точно хочете видалити цей рядок?"):
                del current_table.rows[row_id]
                data_table.delete(selected_item)

        def delete_table():
            if messagebox.askyesno("Підтвердження", "Ви точно хочете видалити цю таблицю?"):
                table_name = table_selector.get()
                if table_name and table_name in database.tables:
                    del database.tables[table_name]
                    table_selector.set("Оберіть таблицю")
                    data_table.delete(*data_table.get_children())
                    for col in data_table["columns"]:
                        data_table.heading(col, text="")
                    dropdown["menu"].delete(table_name)

        def delete_column(event):
            column_id = data_table.identify_column(event.x)
            col_index = int(column_id[1:]) - 1
            col_name = data_table["columns"][col_index]

            if messagebox.askyesno("Підтвердження", f"Ви точно хочете видалити колонку '{col_name}'?"):
                if current_table.delete_column(col_name):
                    data_table.delete(*data_table.get_children())
                    load_table_data()
                else:
                    messagebox.showerror("Помилка", f"Колонка '{col_name}' не знайдена.")

        def save_to_file():
            file_path = filedialog.asksaveasfilename(title="Збережіть файл бази даних", defaultextension=".json",
                                                     filetypes=(("Database Files", "*.json"), ("All Files", "*.*")))
            try:
                if file_path:
                    database.save_to_file(file_path)
                    messagebox.showinfo("Інформація", f"База даних успішно збережена.")
            except Exception:
                messagebox.showinfo("Помилка", f"Неможливо зберегти файл")

        def on_click(event):
            region = data_table.identify_region(event.x, event.y)
            if region == "heading":
                delete_column(event)

        def on_double_click(event):
            region = data_table.identify_region(event.x, event.y)
            if region != "heading":
                edit_row()

        header_frame = tk.Frame(main_window)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        table_names = list(database.tables.keys())

        if table_names:
            table_selector = tk.StringVar(value=table_names[0])
        else:
            table_selector = tk.StringVar(value="Обрати таблицю")

        dropdown = ttk.OptionMenu(header_frame, table_selector, "Обрати таблицю",
                                  *table_names)
        dropdown.pack(side=tk.LEFT, padx=5)

        table_selector.trace("w", load_table_data)

        menu = dropdown["menu"]
        menu.insert_command(0, label="Додати нову таблицю", command=add_new_table)

        tk.Button(header_frame, text="Зберегти", command=save_to_file).pack(side=tk.LEFT, padx=5)
        tk.Button(header_frame, text="Різниця таблиць", command=compare_tables).pack(side=tk.LEFT, padx=5)
        tk.Button(header_frame, text="Додати рядок", command=add_row).pack(side=tk.LEFT, padx=5)
        tk.Button(header_frame, text="Додати колонку", command=add_column).pack(side=tk.LEFT, padx=5)

        table_frame = tk.Frame(main_window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        data_table = ttk.Treeview(table_frame, show="headings")
        data_table.pack(fill=tk.BOTH, expand=True)
        data_table.bind("<Double-1>", on_double_click)
        data_table.bind("<Delete>", lambda event: delete_row())
        data_table.bind("<Button-1>", on_click)

        table_frame = tk.Frame(main_window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        delete_table_button = tk.Button(
            header_frame,
            text="Видалити таблицю",
            command=delete_table,
            bg="#ffcccc",
            fg="black"
        )
        delete_table_button.pack(side=tk.RIGHT, padx=5)

        main_window.mainloop()

    create_button = tk.Button(root, text="Створити БД", command=create_database)
    load_button = tk.Button(root, text="Завантажити БД", command=load_database)

    create_button.pack(pady=10)
    load_button.pack(pady=10)

    root.mainloop()
