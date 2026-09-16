import tkinter
from tkinter import messagebox
import customtkinter
from pytubefix import YouTube
import imageio_ffmpeg
import subprocess
import os

from sub import MP3Page


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("720x550")
        self.title("YouTube Downloader")
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")

        self.container = customtkinter.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for PageClass in (MP4Page, MP3Page):
            page_name = PageClass.__name__
            frame = PageClass(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MP4Page")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class MP4Page(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        nav_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(pady=15)

        mp4_nav_button = customtkinter.CTkButton(
            nav_frame,
            text="MP4 Downloader",
            width=140,
            command=lambda: controller.show_frame("MP4Page")
        )
        mp4_nav_button.pack(side="left", padx=10)

        mp3_nav_button = customtkinter.CTkButton(
            nav_frame,
            text="MP3 Downloader",
            width=140,
            command=lambda: controller.show_frame("MP3Page")
        )
        mp3_nav_button.pack(side="left", padx=10)

        self.label = customtkinter.CTkLabel(
            self,
            text="Welcome to YouTube MP4 Downloader",
            font=("Arial", 20)
        )
        self.label.pack(padx=10, pady=10)

        self.var_link = tkinter.StringVar()
        self.link = customtkinter.CTkEntry(
            self,
            height=40,
            width=400,
            textvariable=self.var_link,
            placeholder_text="Paste YouTube Link (MP4)"
        )
        self.link.pack(pady=10)

        self.percentage = customtkinter.CTkLabel(self, text="0%")
        self.percentage.pack(pady=5)

        self.progressBar = customtkinter.CTkProgressBar(self, width=400)
        self.progressBar.set(0)
        self.progressBar.pack(padx=10, pady=5)

        self.finish = customtkinter.CTkLabel(self, text="")
        self.finish.pack(pady=5)

        self.button = customtkinter.CTkButton(
            self,
            text="Download MP4",
            command=self.startdownload
        )
        self.button.pack(padx=10, pady=10)

    def on_progress(self, stream, chunk, bytes_remaining):
        totalSize = stream.filesize
        bytesDownloaded = totalSize - bytes_remaining
        percentage_of_completion = (bytesDownloaded / totalSize) * 100
        per = str(int(percentage_of_completion))

        self.percentage.configure(text=per + "%")
        self.percentage.update()
        self.progressBar.set(float(percentage_of_completion) / 100)

    def startdownload(self):
        try:
            ytLink = self.link.get().strip()
            if not ytLink:
                messagebox.showwarning("Input Error", "Please enter a valid YouTube link.")
                return

            self.progressBar.set(0)
            self.percentage.configure(text="0%")

            self.finish.configure(
                text="Getting video information...",
                text_color="white"
            )

            ytObject = YouTube(
                ytLink,
                on_progress_callback=self.on_progress
            )

            self.label.configure(text=ytObject.title)

            video = ytObject.streams.filter(
                only_video=True,
                file_extension="mp4"
            ).order_by("resolution").desc().first()

            audio = ytObject.streams.filter(
                only_audio=True
            ).order_by("abr").desc().first()

            if not video or not audio:
                messagebox.showerror("Download Error", "Required video or audio streams were not found.")
                self.finish.configure(
                    text="Stream error occurred.",
                    text_color="red"
                )
                return

            video_file = "temp_video.mp4"
            audio_file = "temp_audio.m4a"

            self.finish.configure(
                text="Downloading video...",
                text_color="white"
            )
            video.download(filename=video_file)

            self.finish.configure(
                text="Downloading audio...",
                text_color="white"
            )
            audio.download(filename=audio_file)

            self.finish.configure(
                text="Merging video and audio...",
                text_color="white"
            )

            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            safe_title = "".join(
                c for c in ytObject.title if c.isalnum() or c in " ._-"
            ).strip()
            output_file = safe_title + ".mp4"

            subprocess.run(
                [
                    ffmpeg, "-y",
                    "-i", video_file,
                    "-i", audio_file,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    output_file
                ],
                check=True
            )

            if os.path.exists(video_file):
                os.remove(video_file)
            if os.path.exists(audio_file):
                os.remove(audio_file)

            self.progressBar.set(1)
            self.percentage.configure(text="100%")
            self.finish.configure(
                text="MP4 Download complete!",
                text_color="green"
            )

        except Exception as e:
            self.finish.configure(text="Error occurred.", text_color="red")
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
