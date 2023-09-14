import os
from flask import Flask, request, jsonify
import json
from tasks import async_download_and_upload_video
import logging
import os
from threading import Thread
logging.basicConfig(level=logging.INFO)
from shared_resources import youtube_videos_collection


app = Flask(__name__)

app.config.update(
    CELERY_BROKER_URL=os.getenv("CELERY_BROKER_URL"),
)


@app.route('/process_video', methods=['POST'])
def process_video():
    data = request.get_json()
    video_url = data.get('video_url')
    public_id = data.get('public_id', 'videos')
    preferred_resolution = data.get('preferred_resolution','360p')


    if video_url:
        task = async_download_and_upload_video.apply_async(args=[video_url, public_id,preferred_resolution])
        response = {
            'status': 'Video processing started',
            'task_id': task.id,
            'video_url': video_url
        }
        return jsonify(response), 202
    else:
        return jsonify({'message': 'Invalid request', 'error': 'video_url is required'}), 400


# A MongoDB's change stream to listen for changes on youtube_videos collection.
def watch_collection():
    with youtube_videos_collection.watch() as stream:
        for change in stream:
            if change['operationType'] == 'insert':
                new_document = change['fullDocument']
                video_url = new_document['video_url']
                public_id = new_document.get('public_id', 'videos')
                preferred_resolution = new_document.get('preferred_resolution', '360p')
                
                async_download_and_upload_video.apply_async(args=[video_url, public_id, preferred_resolution])


if __name__ == "__main__":
    watch_thread = Thread(target=watch_collection)
    watch_thread.start()
    app.run()
