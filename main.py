import yt_dlp

url = input("Enter YouTube URL: ")

# Options for yt-dlp
ydl_opts = {
    "format": "best",          # best available quality
    "outtmpl": "%(title)s.%(ext)s",  # save as video title
    "quiet": True              # suppress logs
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)  # download = False → just fetch info

    print("Title:", info.get("title"))
    print("Views:", info.get("view_count"))
    print("Channel:", info.get("uploader"))
    print("Duration (sec):", info.get("duration"))


print("✅ Download completed!")
