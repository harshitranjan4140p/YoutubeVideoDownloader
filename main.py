import yt_dlp
import tkinter as tk
from tkinter import messagebox, filedialog

# Function to download video/audio
def download_video():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return

    # Ask user for save location
    save_path = filedialog.askdirectory(title="Select Download Folder")
    if not save_path:
        return

    # Options for yt-dlp
    ydl_opts = {
        "outtmpl": f"{save_path}/%(title)s.%(ext)s"
    }

    if download_type.get() == "video":
        ydl_opts["format"] = "best"
    elif download_type.get() == "audio":
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    else:
        messagebox.showerror("Software can only download Video/Audio")
        return

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "Unknown Title")
        messagebox.showinfo("Success", f"Downloaded: {title}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def load_Info():
    
    return

# --- GUI Setup ---
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("400x400")

# URL Label + Entry
tk.Label(root, text="YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Radio buttons for Video/Audio
download_type = tk.StringVar(value="video")
tk.Radiobutton(root, text="Video", variable=download_type, value="video").pack()
tk.Radiobutton(root, text="Audio (MP3)", variable=download_type, value="audio").pack()

# Load Button
tk.Button(root, text="Load Info", command=load_Info, bg="white").pack(pady=15)

# Download Button
tk.Button(root, text="Download", command=download_video, bg="lightblue").pack(pady=15)

root.mainloop()
