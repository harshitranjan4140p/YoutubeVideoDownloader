import yt_dlp
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import requests
from io import BytesIO

videoLoaded = False
videoInfo = None  # to store info globally

# Function to download video/audio
def download_video():
    global videoLoaded, videoInfo
    if not videoLoaded:
        messagebox.showwarning("Warning", "Video/Audio not loaded!!")
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
            ydl.download([videoInfo["webpage_url"]])  # download using stored info
        messagebox.showinfo("Success", f"Downloaded: {videoInfo.get('title', 'Unknown Title')}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Loading Video Info
def load_Info():
    global videoLoaded, videoInfo
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return
    
    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            videoInfo = ydl.extract_info(url, download=False)  # only fetch info
            title = videoInfo.get("title", "Unknown Title")
            views = videoInfo.get("view_count", 0)
            likes = videoInfo.get("like_count", "N/A")
            thumb_url = videoInfo.get("thumbnail")

        # Update GUI labels
        title_label.config(text=f"Title: {title}")
        views_label.config(text=f"Views: {views:,}")
        likes_label.config(text=f"Likes: {likes if likes != 'N/A' else 'Hidden'}")

        # Load thumbnail if available
        if thumb_url:
            response = requests.get(thumb_url)
            img_data = Image.open(BytesIO(response.content))
            img_data = img_data.resize((200, 120))  # resize for display
            thumb_img = ImageTk.PhotoImage(img_data)
            thumbnail_label.config(image=thumb_img)
            thumbnail_label.image = thumb_img  # keep reference

        videoLoaded = True
        messagebox.showinfo("Loaded", "Video info loaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        videoLoaded = False

# --- GUI Setup ---
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("450x500")

# URL Label + Entry
tk.Label(root, text="YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Radio buttons for Video/Audio
download_type = tk.StringVar(value="video")
tk.Radiobutton(root, text="Video", variable=download_type, value="video").pack()
tk.Radiobutton(root, text="Audio (MP3)", variable=download_type, value="audio").pack()

# Load Button
tk.Button(root, text="Load Info", command=load_Info, bg="white").pack(pady=10)

# Labels for video info
title_label = tk.Label(root, text="Title: -", wraplength=400, justify="left")
title_label.pack(pady=5)

views_label = tk.Label(root, text="Views: -")
views_label.pack(pady=5)

likes_label = tk.Label(root, text="Likes: -")
likes_label.pack(pady=5)

# Thumbnail Display
thumbnail_label = tk.Label(root)
thumbnail_label.pack(pady=10)

# Download Button
tk.Button(root, text="Download", command=download_video, bg="lightblue").pack(pady=15)

root.mainloop()
