from dotenv import load_dotenv
load_dotenv()
import subprocess
import cloudinary
import cloudinary.api
from cloudinary import CloudinaryImage,uploader
import json
config = cloudinary.config(secure=True)
from celery import Celery
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
import logging
import os
import subprocess
from shared_resources import results_collection


celery = Celery('tasks', broker=os.getenv("CELERY_BROKER_URL"))

def upload_progress_handler(progress_percentage, bytes_uploaded, total_bytes, upload_id):
    logging.info(f'Upload progress: {progress_percentage}% ({bytes_uploaded}/{total_bytes} bytes)')



def save_result_to_mongo(video_url,original_size,processed_size,ffmpeg_config,processing_error):
    doc = {
      "video_url": video_url,
        "original_size": original_size/1e+6, # convert byte to megabyte
        "processed_size": processed_size / 1e+6,
        "ffmpeg_config": ffmpeg_config,
        "processing_error": processing_error
    }
    results_collection.insert_one(doc)

def process_video_with_ffmpeg(ffmpeg_config):

    result = subprocess.run(ffmpeg_config, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        # Handle error
        error_message = f"Error processing video: {result.stderr.decode('utf-8')}"
        logging.error(error_message)
        return error_message
    return None  # return None if the operation was successful

def get_youtube_video(video_url: str) -> YouTube:
    """Retrieve YouTube video object."""
    try:
        return YouTube(video_url)
    except VideoUnavailable:
        logging.error(f'Video {video_url} is unavailable, skipping.')
        return None


def get_video_stream(yt: YouTube, resolution: str = "720p"):
    """Retrieve the video stream based on the resolution."""
    return yt.streams.filter(progressive=True, res=resolution).order_by('resolution').asc().first()


def build_cloudinary_url(public_id: str) -> str:
    """Build and return the Cloudinary URL based on the public ID."""
    return CloudinaryImage(public_id).build_url()


def upload_video(path: str, public_id: str) -> str:
    """Upload the video to Cloudinary and return the video URL."""
    try:
        response = uploader.upload(
            path,
            public_id=public_id,
            unique_filename=False,
            overwrite=True,
            resource_type="video",
            progress_callback=upload_progress_handler
        )
        if 'secure_url' in response:
            logging.info(f"Delivery URL: {response['secure_url']}")
            return response['secure_url']
        else:
            logging.error("Failed to upload video: Invalid response from Cloudinary")
            return ''
    except Exception as e:
        logging.error(f"Failed to upload video due to: {e}")
        return ''


def cleanup_downloaded_file(path: str) -> None:
    """Delete the downloaded file if it exists."""
    if os.path.exists(path):
        os.remove(path)
        logging.info(f"Cleaned up downloaded file: {path}")


@celery.task(bind=True)
def async_download_and_upload_video(self, video_url: str, public_id: str, preferred_resolution: str ) -> str:
    """Download the video from YouTube and upload it to Cloudinary, returning the video URL."""
    yt = get_youtube_video(video_url)
    if yt:
        logging.info('Downloading %s', yt.title)
        video_path = yt.video_id + ".mp4"
        output_path = "processed_" + video_path
        video_stream = get_video_stream(yt,preferred_resolution)
        
        if video_stream:
            video_stream.download(filename=video_path)
            # Get the size of the original video
            original_size = os.path.getsize(video_path)

            ffmpeg_config = [
            "ffmpeg", 
            "-i", video_path, 
            "-vf", "scale=-2:360",
            "-c:v", "libx264", 
            "-preset", "veryslow", # better compression but will be slower
            "-crf", "30",
            "-c:a", "aac", 
            "-b:a", "128k", # bitrate for the audio
            "-vcodec","libx264",
            output_path
            ]

            
            # Process the video with FFmpeg before uploading
            error_message = process_video_with_ffmpeg(ffmpeg_config)
            if error_message:
                # If there was an error in the FFmpeg processing, return the error message
                save_result_to_mongo(
                video_url= video_url,
                original_size= original_size,
                processed_size= 0,
                ffmpeg_config= ffmpeg_config,
                processing_error= error_message
                )
                return error_message

            # Get the size of the processed video
            processed_size = os.path.getsize(output_path)

            # Upload the processed video to Cloudinary
            video_url = upload_video(output_path, public_id)
            # Save the result to MongoDB
            save_result_to_mongo(
                video_url= video_url,
                original_size= original_size,
                processed_size= processed_size,
                ffmpeg_config= ffmpeg_config,
                processing_error= error_message
            )
            cleanup_downloaded_file(video_path)
            cleanup_downloaded_file(output_path)  # Clean up the processed file as well
            return video_url
        else:
            logging.error("No video stream found with the specified resolution")
            return ''
    else:
        return ''





