import os
import shutil
import threading
import time
import webbrowser
from tkinter import Tk, Label, Button, filedialog, messagebox, ttk, StringVar
import ctypes

class FileCopierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Copier")

        # Labels and buttons for browsing directories
        self.label1 = Label(root, text="Select Source Directory")
        self.label1.pack(pady=5)

        self.src_button = Button(root, text="Browse Source", command=self.browse_src)
        self.src_button.pack(pady=5)

        self.label2 = Label(root, text="Select Destination Directory")
        self.label2.pack(pady=5)

        self.dest_button = Button(root, text="Browse Destination", command=self.browse_dest)
        self.dest_button.pack(pady=5)

        # Copy button
        self.copy_button = Button(root, text="Copy Files", command=self.start_copy_thread)
        self.copy_button.pack(pady=20)

        # Progress bar and percentage label
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.percentage_var = StringVar()
        self.percentage_label = Label(root, textvariable=self.percentage_var)
        self.percentage_label.pack(pady=5)

        # Transfer rate label
        self.rate_label_var = StringVar()
        self.rate_label = Label(root, textvariable=self.rate_label_var)
        self.rate_label.pack(pady=5)

        # Description and credits
        self.description_label = Label(root, text="This program copies/dumps all files from a selected directory and its subdirectories to a destination folder.")
        self.description_label.pack(pady=10)

        self.link_label = Label(root, text="Program Made By https://256bits.tech", fg="blue", cursor="hand2")
        self.link_label.pack(pady=5)
        self.link_label.bind("<Button-1>", self.open_link)

        self.src_dir = ""
        self.dest_dir = ""
        self.file_list = []
        self.copy_in_progress = False  # Flag to track if copying is in progress

    def browse_src(self):
        self.src_dir = filedialog.askdirectory()
        if self.src_dir:
            messagebox.showinfo("Selected Source", f"Source Directory: {self.src_dir}")

    def browse_dest(self):
        self.dest_dir = filedialog.askdirectory()
        if self.dest_dir:
            messagebox.showinfo("Selected Destination", f"Destination Directory: {self.dest_dir}")

    def get_files(self, dir_path):
        """Recursively get all file paths from a directory and its subdirectories."""
        file_paths = []
        for root_dir, _, files in os.walk(dir_path):
            for file in files:
                file_paths.append(os.path.join(root_dir, file))
        return file_paths

    def copy_files(self):
        # Prevent starting another copy while one is in progress
        if self.copy_in_progress:
            return

        if not self.src_dir or not self.dest_dir:
            messagebox.showwarning("Missing Information", "Please select both source and destination directories.")
            self.copy_in_progress = False
            return

        self.copy_in_progress = True
        self.copy_button.config(state="disabled")  # Disable the button during the copy process

        # Get list of files
        self.file_list = self.get_files(self.src_dir)

        if not self.file_list:
            messagebox.showinfo("No Files", "No files found in the selected source directory.")
            self.copy_in_progress = False
            self.copy_button.config(state="normal")  # Re-enable the button if no files found
            return

        # Configure the progress bar
        self.progress["maximum"] = len(self.file_list)
        self.progress["value"] = 0

        total_bytes = 0
        try:
            for idx, file_path in enumerate(self.file_list):
                dest_file_path = os.path.join(self.dest_dir, os.path.basename(file_path))

                # Measure time and bytes transferred
                start_time = time.time()
                bytes_transferred = os.path.getsize(file_path)
                shutil.copy2(file_path, dest_file_path)
                end_time = time.time()

                total_bytes += bytes_transferred
                duration = end_time - start_time

                # Update progress bar and percentage
                self.progress["value"] = idx + 1
                percentage_done = (idx + 1) / len(self.file_list) * 100
                self.percentage_var.set(f"{percentage_done:.2f}% done")

                self.root.update_idletasks()

                # Calculate transfer rate (MB/s)
                if duration > 0:
                    transfer_rate = (bytes_transferred / (1024 * 1024)) / duration
                    self.rate_label_var.set(f"Transfer rate: {transfer_rate:.2f} MB/s")

            messagebox.showinfo("Success", "Files copied successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.copy_in_progress = False  # Reset the flag when copying is done
            self.copy_button.config(state="normal")  # Re-enable the button

    def start_copy_thread(self):
        if not self.copy_in_progress:  # Only allow starting a copy if none are in progress
            copy_thread = threading.Thread(target=self.copy_files)
            copy_thread.start()

    def open_link(self, event):
        webbrowser.open_new("https://256bits.tech")  # Open the link in a web browser

if __name__ == "__main__":
    # Enable Windows file drag-and-drop behavior
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("file_copier_app")

    root = Tk()
    app = FileCopierApp(root)
    root.mainloop()
