import yt_dlp
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Global flags and storage
videoLoaded = False
videoInfo = None  # Stores video info for later download


# ------------------ Progress Hook ------------------
def progress_hook(d):
    """
    Called automatically by yt-dlp during download.
    Updates the progress bar and status label in GUI.
    """
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            percent_val = downloaded / total * 100
            progress_bar['value'] = percent_val
            status_label.config(text=f"Downloading... {percent_val:.1f}%")
            root.update_idletasks()  # Refresh GUI
    elif d['status'] == 'finished':
        progress_bar['value'] = 100
        status_label.config(text="Download complete!")


# ------------------ Download Function ------------------
def download_video():
    """
    Downloads the video to user-selected folder.
    (This will block the GUI until download is finished since threading is removed.)
    """
    global videoLoaded, videoInfo
    if not videoLoaded:
        messagebox.showwarning("Warning", "Video not loaded!!")
        return
    
    # Ask user where to save the file
    save_path = filedialog.askdirectory(title="Select Download Folder")
    if not save_path:
        return
    
    # yt-dlp options
    ydl_opts = {
        "format": "best",  # best available quality
        "outtmpl": f"{save_path}/%(title)s.%(ext)s",  # Save as Title.ext
        "progress_hooks": [progress_hook],  # Attach hook for progress bar
        "noprogress": True
    }

    # Reset progress bar
    progress_bar['value'] = 0

    try:
        # Start download (this blocks the GUI until finished)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([videoInfo["webpage_url"]])
        messagebox.showinfo("Success", f"Downloaded: {videoInfo.get('title', 'Unknown Title')}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# ------------------ Load Video Info ------------------
def load_Info():
    """
    Extracts video information (title, views, likes, thumbnail)
    and updates the GUI with details.
    """
    global videoLoaded, videoInfo
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return
    
    try:
        # Extract video metadata
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            videoInfo = ydl.extract_info(url, download=False)
            title = videoInfo.get("title", "Unknown Title")
            views = videoInfo.get("view_count", 0)
            likes = videoInfo.get("like_count", "N/A")
            thumb_url = videoInfo.get("thumbnail")

        # Update labels with metadata
        title_label.config(text=f"Title: {title}")
        views_label.config(text=f"Views: {views:,}")
        likes_label.config(text=f"Likes: {likes if likes != 'N/A' else 'Hidden'}")

        # Load thumbnail image
        if thumb_url:
            response = requests.get(thumb_url)
            img_data = Image.open(BytesIO(response.content))
            img_data = img_data.resize((200, 120))  # Resize to fit
            thumb_img = ImageTk.PhotoImage(img_data)
            thumbnail_label.config(image=thumb_img)
            thumbnail_label.image = thumb_img

        videoLoaded = True
        status_label.config(text="Video info loaded. Ready to download.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        videoLoaded = False


# ------------------ GUI Setup ------------------
root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("450x600")

# URL Entry
tk.Label(root, text="YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

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

# Status Label
status_label = tk.Label(root, text="Status: Idle", fg="blue")
status_label.pack(pady=10)

# Progress Bar
progress_bar = ttk.Progressbar(root, length=300, mode='determinate')
progress_bar.pack(pady=10)

# Download Button
tk.Button(root, text="Download Video", command=download_video, bg="lightblue").pack(pady=15)

# Start GUI loop
root.mainloop()
