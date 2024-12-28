from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import yt_dlp
import logging
import re

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# Adding CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the current directory to save the downloaded videos
cur_dir = os.getcwd()

# Directory to save downloaded videos
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.post("/download")
async def download_video(link: str = Form(...)):
    try:
        # Validate YouTube URL using a regex to ensure it's a valid video URL
        youtube_url_pattern = r"(https?://(?:www\.)?youtube\.com/watch\?v=[\w-]{11}|https?://(?:www\.)?youtu\.be/[\w-]{11})"
        if not re.match(youtube_url_pattern, link):
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        logging.debug(f"Received YouTube URL: {link}")

        # Define the yt-dlp download options
        youtube_dl_options = {
            "format": "bestvideo+bestaudio/best",  # Download best video and best audio
            "outtmpl": os.path.join(DOWNLOAD_DIR, f"video-{link[-11:]}.mp4"),  # Path to save the file
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",  # Convert to MP4 if needed
                "preferedformat": "mp4",  # Use MP4 codec for the output
            }],
        }

        # Using yt-dlp to download the video
        with yt_dlp.YoutubeDL(youtube_dl_options) as ydl:
            try:
                ydl.download([link])
            except yt_dlp.DownloadError as e:
                logging.error(f"yt-dlp download error: {str(e)}")
                raise HTTPException(status_code=500, detail="Error downloading video with yt-dlp")

        # Define the path to the downloaded file
        download_file_path = os.path.join(DOWNLOAD_DIR, f"video-{link[-11:]}.mp4")

        logging.debug(f"Video downloaded successfully: {download_file_path}")
        return {"status": "success", "download_url": download_file_path}

    except Exception as e:
        logging.error(f"Error during video download: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")
