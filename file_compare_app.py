import os
import filecmp
import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib

class FileCompareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Compare Utility")

        # Цветовая палитра
        bg_color = "#F0F0F0"
        button_color = "#4CAF50"
        text_color = "#333333"

        # Создаем кнопки и размещаем их на главном окне
        self.label1 = tk.Label(root, text="Directory 1:", bg=bg_color, fg=text_color)
        self.label1.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry1 = tk.Entry(root, width=50)
        self.entry1.grid(row=0, column=1, padx=10, pady=10)
        self.browse_button1 = tk.Button(root, text="Browse", command=self.browse_directory1, bg=button_color, fg="white")
        self.browse_button1.grid(row=0, column=2, padx=10, pady=10)

        self.label2 = tk.Label(root, text="Directory 2:", bg=bg_color, fg=text_color)
        self.label2.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry2 = tk.Entry(root, width=50)
        self.entry2.grid(row=1, column=1, padx=10, pady=10)
        self.browse_button2 = tk.Button(root, text="Browse", command=self.browse_directory2, bg=button_color, fg="white")
        self.browse_button2.grid(row=1, column=2, padx=10, pady=10)

        self.compare_button = tk.Button(root, text="Compare", command=self.compare_directories, bg=button_color, fg="white")
        self.compare_button.grid(row=2, column=1, pady=20)

        # Добавляем Text widget для вывода результата
        self.result_text = tk.Text(root, height=10, width=70)
        self.result_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Установка цветовой палитры для Text widget
        self.result_text.configure(bg=bg_color, fg=text_color)

    def browse_directory1(self):
        directory1 = filedialog.askdirectory()
        self.entry1.delete(0, tk.END)
        self.entry1.insert(0, directory1)

    def browse_directory2(self):
        directory2 = filedialog.askdirectory()
        self.entry2.delete(0, tk.END)
        self.entry2.insert(0, directory2)

    def compare_directories(self):
        directory1 = self.entry1.get()
        directory2 = self.entry2.get()

        if not directory1 or not directory2:
            messagebox.showerror("Error", "Please select both directories.")
            return

        if not os.path.exists(directory1) or not os.path.exists(directory2):
            messagebox.showerror("Error", "Selected directories do not exist.")
            return

        dcmp = filecmp.dircmp(directory1, directory2)

        # Очищаем предыдущий вывод
        self.result_text.delete(1.0, tk.END)

        # Выводим результат в Text widget
        self.result_text.insert(tk.END, f"Files only in {directory1}:\n{dcmp.left_only}\n\n")
        self.result_text.insert(tk.END, f"Files only in {directory2}:\n{dcmp.right_only}\n\n")
        self.result_text.insert(tk.END, f"Differing files:\n{dcmp.diff_files}\n\n")

        # Проверка размера файла и использование хеш-сумм
        for file_name in dcmp.common_files:
            file_path1 = os.path.join(directory1, file_name)
            file_path2 = os.path.join(directory2, file_name)

            # Проверка размера файла перед открытием
            if os.path.getsize(file_path1) > 100 * 1024 * 1024 or os.path.getsize(file_path2) > 100 * 1024 * 1024:
                self.result_text.insert(tk.END, f"File size exceeds the maximum limit (100 MB): {file_name}\n")
                continue

            # Получение хеш-сумм файлов
            hash1 = self.get_file_hash(file_path1)
            hash2 = self.get_file_hash(file_path2)

            # Сравнение хеш-сумм
            if hash1 != hash2:
                self.result_text.insert(tk.END, f"Files differ: {file_name}\n")

    def get_file_hash(self, file_path):
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileCompareApp(root)
    root.mainloop()
