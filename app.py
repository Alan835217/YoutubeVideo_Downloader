import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import threading
import os
import requests
from PIL import Image, ImageTk
from io import BytesIO

FFMPEG_PATH = r"C:\ffmpeg-2026-02-26-git-6695528af6-full_build\bin"

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Youtube Video Downloader")
        self.root.geometry("620x700")
        self.root.configure(bg="#1e1e2f")

        self.url_var = tk.StringVar()
        self.save_path = os.getcwd()
        self.format_dict = {}

        self.build_ui()

    # ---------------- UI ----------------
    def build_ui(self):
        title = tk.Label(
            self.root,
            text="Youtube Video Downloader",
            font=("Segoe UI", 20, "bold"),
            bg="#1e1e2f",
            fg="white"
        )
        title.pack(pady=20)

        url_entry = tk.Entry(
            self.root,
            textvariable=self.url_var,
            font=("Segoe UI", 12),
            width=55
        )
        url_entry.pack(pady=10)

        fetch_btn = tk.Button(
            self.root,
            text="Fetch Video",
            command=self.fetch_info,
            bg="#6c5ce7",
            fg="white",
            font=("Segoe UI", 11),
            width=20
        )
        fetch_btn.pack(pady=10)

        self.thumbnail_label = tk.Label(self.root, bg="#1e1e2f")
        self.thumbnail_label.pack(pady=10)

        self.title_label = tk.Label(
            self.root,
            bg="#1e1e2f",
            fg="white",
            wraplength=550
        )
        self.title_label.pack(pady=5)

        self.quality_box = ttk.Combobox(self.root, state="readonly", width=30)
        self.quality_box.pack(pady=10)

        self.audio_var = tk.BooleanVar()
        audio_check = tk.Checkbutton(
            self.root,
            text="Audio Only (MP3)",
            variable=self.audio_var,
            bg="#1e1e2f",
            fg="white",
            selectcolor="#1e1e2f"
        )
        audio_check.pack()

        path_btn = tk.Button(
            self.root,
            text="Choose Save Location",
            command=self.choose_path,
            bg="#00b894",
            fg="white",
            font=("Segoe UI", 10)
        )
        path_btn.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, length=450)
        self.progress.pack(pady=10)

        self.progress_label = tk.Label(self.root, bg="#1e1e2f", fg="white")
        self.progress_label.pack()

        self.speed_label = tk.Label(self.root, bg="#1e1e2f", fg="white")
        self.speed_label.pack()

        download_btn = tk.Button(
            self.root,
            text="Download",
            command=self.start_download,
            bg="#e17055",
            fg="white",
            font=("Segoe UI", 12),
            width=20
        )
        download_btn.pack(pady=20)

    # ---------------- Fetch Video Info ----------------
    def fetch_info(self):
        url = self.url_var.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return

        try:
            ydl_opts = {"quiet": True}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            self.title_label.config(text=info.get("title"))

            # Thumbnail
            response = requests.get(info.get("thumbnail"))
            img_data = Image.open(BytesIO(response.content))
            img_data = img_data.resize((480, 270))
            self.thumbnail = ImageTk.PhotoImage(img_data)
            self.thumbnail_label.config(image=self.thumbnail)

            # Formats
            formats = []
            self.format_dict.clear()

            for f in info["formats"]:
                if f.get("height") and f.get("vcodec") != "none":
                    quality = f"{f['height']}p"
                    if quality not in formats:
                        formats.append(quality)
                        self.format_dict[quality] = f["format_id"]

            self.quality_box["values"] = formats
            if formats:
                self.quality_box.current(0)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- Choose Folder ----------------
    def choose_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_path = folder

    # ---------------- Start Download Thread ----------------
    def start_download(self):
        threading.Thread(target=self.download_video).start()

    # ---------------- Download Logic ----------------
    def download_video(self):
        url = self.url_var.get()

        def hook(d):
            if d["status"] == "downloading":
                percent = d.get("_percent_str", "0%").strip()
                speed = d.get("_speed_str", "")

                self.progress_label.config(text=f"Progress: {percent}")
                self.speed_label.config(text=f"Speed: {speed}")

                try:
                    value = float(percent.replace("%", ""))
                    self.progress["value"] = value
                except:
                    pass

        try:
            if self.audio_var.get():
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": f"{self.save_path}/%(title)s.%(ext)s",
                    "ffmpeg_location": FFMPEG_PATH,
                    "progress_hooks": [hook],
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio"
                    }]
                }
            else:
                quality = self.quality_box.get()
                format_id = self.format_dict.get(quality)

                ydl_opts = {
                    "format": f"{format_id}+bestaudio/best",
                    "outtmpl": f"{self.save_path}/%(title)s.%(ext)s",
                    "merge_output_format": "mp4",
                    "ffmpeg_location": FFMPEG_PATH,
                    "progress_hooks": [hook]
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            messagebox.showinfo("Success", "Download Completed!")

        except Exception as e:
            messagebox.showerror("Download Error", str(e))


# ---------------- Run App ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()