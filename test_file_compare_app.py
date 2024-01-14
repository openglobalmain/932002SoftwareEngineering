import unittest
from unittest.mock import patch
from io import StringIO
from tempfile import TemporaryDirectory
import os
import shutil
import tkinter as tk
from file_compare_app import FileCompareApp


class TestFileCompareApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()

    def tearDown(self):
        self.root.destroy()
    # Выбор пустых директорий

    def test_empty_directories(self):
        with TemporaryDirectory() as tempdir1, TemporaryDirectory() as tempdir2:
            app = FileCompareApp(self.root)

            with patch('tkinter.filedialog.askdirectory', side_effect=[tempdir1, tempdir2]):
                app.browse_directory1()
                app.browse_directory2()

            with patch('tkinter.messagebox.showerror') as mock_error:
                app.compare_directories()

            mock_error.assert_called_once_with(
                "Error", "No files to compare. Please select directories with files.")
            self.assertEqual(app.result_text.get("1.0", tk.END), "")

    # Выбор директорий с одинаковыми файлами
    def test_identical_files(self):
        with TemporaryDirectory() as tempdir:
            file1_path = os.path.join(tempdir, "file1.txt")
            file2_path = os.path.join(tempdir, "file2.txt")
            content = "Test content"

            with open(file1_path, 'w') as file1, open(file2_path, 'w') as file2:
                file1.write(content)
                file2.write(content)

            app = FileCompareApp(self.root)

            with patch('tkinter.filedialog.askdirectory', return_value=tempdir):
                app.browse_directory1()
                app.browse_directory2()

            with patch('tkinter.messagebox.showerror') as mock_error:
                app.compare_directories()

            mock_error.assert_not_called()
            expected_result = f"Files only in {tempdir}:\n\nFiles only in {tempdir}:\n\nDiffering files:\n\n"
            self.assertEqual(app.result_text.get(
                "1.0", tk.END), expected_result)
        # Выбор директорий с различающимися файлами

    def test_different_files(self):
        with TemporaryDirectory() as tempdir:
            file1_path = os.path.join(tempdir, "file1.txt")
            file2_path = os.path.join(tempdir, "file2.txt")

            with open(file1_path, 'w') as file1, open(file2_path, 'w') as file2:
                file1.write("Content 1")
                file2.write("Content 2")

            app = FileCompareApp(self.root)

            with patch('tkinter.filedialog.askdirectory', return_value=tempdir):
                app.browse_directory1()
                app.browse_directory2()

            with patch('tkinter.messagebox.showerror') as mock_error:
                app.compare_directories()

            mock_error.assert_not_called()
            expected_result = f"Files only in {tempdir}:\n\nFiles only in {tempdir}:\n\nDiffering files:\nfile1.txt\n"
            self.assertEqual(app.result_text.get(
                "1.0", tk.END), expected_result)
    # Выбор только одной директории

    def test_one_directory_selected(self):
        with TemporaryDirectory() as tempdir:
            app = FileCompareApp(self.root)

            with patch('tkinter.filedialog.askdirectory', return_value=tempdir):
                app.browse_directory1()

            with patch('tkinter.messagebox.showerror') as mock_error:
                app.compare_directories()

            mock_error.assert_called_once_with(
                "Error", "Please select both directories.")
            self.assertEqual(app.result_text.get("1.0", tk.END), "")
    # Выбор несуществующей директории

    def test_nonexistent_directory_selected(self):
        nonexistent_dir = "/nonexistent/directory"
        app = FileCompareApp(self.root)

        with patch('tkinter.filedialog.askdirectory', return_value=nonexistent_dir):
            app.browse_directory1()
            app.browse_directory2()

        with patch('tkinter.messagebox.showerror') as mock_error:
            app.compare_directories()

        mock_error.assert_called_once_with(
            "Error", "Selected directories do not exist.")
        self.assertEqual(app.result_text.get("1.0", tk.END), "")
    # Выбор директорий с большими файлами

    def test_large_files_selected(self):
        with TemporaryDirectory() as tempdir:
            file1_path = os.path.join(tempdir, "large_file1.txt")
            file2_path = os.path.join(tempdir, "large_file2.txt")

            with open(file1_path, 'wb') as file1, open(file2_path, 'wb') as file2:
                file1.write(b'A' * (100 * 1024 * 1024 + 1))
                file2.write(b'B' * (100 * 1024 * 1024 + 1))

            app = FileCompareApp(self.root)

            with patch('tkinter.filedialog.askdirectory', return_value=tempdir):
                app.browse_directory1()
                app.browse_directory2()

            with patch('tkinter.messagebox.showerror') as mock_error:
                app.compare_directories()

            mock_error.assert_called_once_with(
                "Error", "File size exceeds the maximum limit (100 MB): large_file1.txt\n")
            self.assertEqual(app.result_text.get("1.0", tk.END), "")
    # Выбор директорий с файлами, у которых различаются хеш-суммы

    def test_files_with_different_hashes(self):
        with TemporaryDirectory() as tempdir:
            file1_path = os.path.join(tempdir, "file1.txt")
            file2_path = os.path.join(tempdir, "file2.txt")

            with open(file1_path, 'w') as file1, open(file2_path, 'w') as file2:
                file1.write("Content 1")
                file2.write("Content 2")

            app = FileCompareApp(self.root)

            with patch('tkinter.filedialog.askdirectory', return_value=tempdir):
                app.browse_directory1()
                app.browse_directory2()

            with patch('tkinter.messagebox.showerror') as mock_error:
                app.compare_directories()

            mock_error.assert_not_called()
            expected_result = f"Files only in {tempdir}:\n\nFiles only in {tempdir}:\n\nDiffering files:\nfile1.txt\n"
            expected_result += "Files differ: file1.txt\n"
            self.assertEqual(app.result_text.get(
                "1.0", tk.END), expected_result)


if __name__ == '__main__':
    unittest.main()
