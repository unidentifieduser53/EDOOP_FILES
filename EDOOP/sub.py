import tkinter
import customtkinter
from CTkMessagebox import CTkMessagebox
from pytubefix import YouTube
import imageio_ffmpeg
import subprocess
import os


class MP3Page(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Navigation Buttons Frame (Centered at the Top)
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

        # Title
        self.label = customtkinter.CTkLabel(
            self,
            text="YouTube to MP3 Converter",
            font=("Arial", 20)
        )
        self.label.pack(padx=10, pady=10)

        # Link Entry
        self.var_link = tkinter.StringVar()
        self.link = customtkinter.CTkEntry(
            self,
            height=40,
            width=400,
            textvariable=self.var_link,
            placeholder_text="Paste YouTube Link (MP3)"
        )
        self.link.pack(pady=10)

        # Progress Percentage Label
        self.percentage = customtkinter.CTkLabel(self, text="0%")
        self.percentage.pack(pady=5)

        # Progress Bar
        self.progressBar = customtkinter.CTkProgressBar(self, width=400)
        self.progressBar.set(0)
        self.progressBar.pack(padx=10, pady=5)

        # Status Label
        self.finish = customtkinter.CTkLabel(self, text="")
        self.finish.pack(pady=5)

        # Download Button
        self.button = customtkinter.CTkButton(
            self,
            text="Download MP3",
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
                CTkMessagebox(
                    title="Input Error",
                    message="Please enter a valid YouTube link.",
                    icon="warning"
                )
                return

            self.progressBar.set(0)
            self.percentage.configure(text="0%")

            self.finish.configure(
                text="Getting audio information...",
                text_color="white"
            )

            ytObject = YouTube(
                ytLink,
                on_progress_callback=self.on_progress
            )

            self.label.configure(text=ytObject.title)
            audio = ytObject.streams.get_audio_only()

            if audio is None:
                CTkMessagebox(
                    title="Download Error",
                    message="No valid audio stream found.",
                    icon="cancel"
                )
                self.finish.configure(
                    text="No audio stream found.",
                    text_color="red"
                )
                return

            self.finish.configure(
                text="Downloading audio...",
                text_color="white"
            )

            temp_audio = "temp_audio.m4a"
            audio.download(filename=temp_audio)

            self.finish.configure(
                text="Converting to MP3...",
                text_color="white"
            )

            safe_title = "".join(
                c for c in ytObject.title if c.isalnum() or c in " ._-"
            ).strip()
            output_file = safe_title + ".mp3"

            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            subprocess.run(
                [
                    ffmpeg, "-y",
                    "-i", temp_audio,
                    "-vn",
                    "-codec:a", "libmp3lame",
                    "-b:a", "192k",
                    output_file
                ],
                check=True
            )

            if os.path.exists(temp_audio):
                os.remove(temp_audio)

            self.progressBar.set(1)
            self.percentage.configure(text="100%")
            self.finish.configure(
                text="MP3 Download Complete!",
                text_color="green"
            )

        except Exception as e:
            self.finish.configure(text="Error occurred.", text_color="red")
            CTkMessagebox(
                title="Error",
                message=f"An unexpected error occurred:\n{e}",
                icon="cancel"
            )