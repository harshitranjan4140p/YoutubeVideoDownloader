import yt_dlp
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading

videoLoaded = False
videoInfo = None  # store video info globally

# --- Progress hook for yt-dlp ---
def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            percent_val = downloaded / total * 100
            progress_bar.after(0, lambda: progress_bar.config(value=percent_val))
            status_label.after(0, lambda: status_label.config(
                text=f"Downloading... {percent_val:.1f}%"
            ))
    elif d['status'] == 'finished':
        progress_bar.after(0, lambda: progress_bar.config(value=100))
        status_label.after(0, lambda: status_label.config(text="Download complete!"))

# --- Function to get format string ---
def get_format_code(choice):
    format_map = {
        "Best Available": "best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
        "Audio Only": "bestaudio/best"
    }
    return format_map.get(choice, "best")

# --- Function to show file size when quality changes ---
def update_file_size(*args):
    global videoInfo
    if not videoInfo:
        return
    quality_choice = quality_var.get()
    format_code = get_format_code(quality_choice)
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            formats = videoInfo.get("formats", [])
            # let yt-dlp pick the matching format
            selected = ydl.build_format_selector(format_code)(videoInfo)
            if selected:
                fmt = selected[0]
                size = fmt.get("filesize") or fmt.get("filesize_approx")
                if size:
                    size_mb = size / (1024 * 1024)
                    size_label.config(text=f"Estimated Size: {size_mb:.2f} MB")
                else:
                    size_label.config(text="Estimated Size: Unknown")
            else:
                size_label.config(text="Estimated Size: Unknown")
    except Exception:
        size_label.config(text="Estimated Size: Unknown")

# --- Function to download video (runs in a thread) ---
def download_video():
    global videoLoaded, videoInfo
    if not videoLoaded:
        messagebox.showwarning("Warning", "Video not loaded!!")
        return
    
    save_path = filedialog.askdirectory(title="Select Download Folder")
    if not save_path:
        return

    quality_choice = quality_var.get()
    format_code = get_format_code(quality_choice)

    ydl_opts = {
        "format": format_code,
        "outtmpl": f"{save_path}/%(title)s.%(ext)s",
        "progress_hooks": [progress_hook],
        "noprogress": True,
        "socket_timeout": 30,
        "retries": 10,
        "fragment_retries": 10,
        "continuedl": True,
        "ignoreerrors": True
    }

    def run_download():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([videoInfo["webpage_url"]])
            messagebox.showinfo("Success", f"Downloaded: {videoInfo.get('title', 'Unknown Title')}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    threading.Thread(target=run_download, daemon=True).start()

# --- Loading video info ---
def load_Info():
    global videoLoaded, videoInfo
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return
    
    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            videoInfo = ydl.extract_info(url, download=False)
            title = videoInfo.get("title", "Unknown Title")
            thumb_url = videoInfo.get("thumbnail")

        # Update GUI labels
        title_label.config(text=f"Title: {title}")

        # Load thumbnail
        if thumb_url:
            response = requests.get(thumb_url)
            img_data = Image.open(BytesIO(response.content))
            img_data = img_data.resize((200, 120))
            thumb_img = ImageTk.PhotoImage(img_data)
            thumbnail_label.config(image=thumb_img)
            thumbnail_label.image = thumb_img

        videoLoaded = True
        status_label.config(text="Video info loaded. Ready to download.")
        update_file_size()  # show initial size based on default quality
    except Exception as e:
        messagebox.showerror("Error", str(e))
        videoLoaded = False

# --- GUI Setup ---
root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("450x650")

# URL Label + Entry
tk.Label(root, text="YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Load Button
tk.Button(root, text="Load Info", command=load_Info, bg="white").pack(pady=10)

# Labels for video info
title_label = tk.Label(root, text="Title: -", wraplength=400, justify="left")
title_label.pack(pady=5)

# Thumbnail Display
thumbnail_label = tk.Label(root)
thumbnail_label.pack(pady=10)

# Quality Selection
tk.Label(root, text="Select Quality:").pack(pady=5)
quality_var = tk.StringVar(value="Best Available")
quality_dropdown = ttk.Combobox(root, textvariable=quality_var, state="readonly",
                                values=["Best Available", "1080p", "720p", "480p", "Audio Only"])
quality_dropdown.pack(pady=5)
quality_var.trace("w", update_file_size)  # update size when quality changes

# Estimated size label
size_label = tk.Label(root, text="Estimated Size: -")
size_label.pack(pady=5)

# Status Label
status_label = tk.Label(root, text="Status: Idle", fg="blue")
status_label.pack(pady=10)

# Progress Bar
progress_bar = ttk.Progressbar(root, length=300, mode='determinate')
progress_bar.pack(pady=10)

# Download Button
tk.Button(root, text="Download Video", command=download_video, bg="lightblue").pack(pady=15)

root.mainloop()
