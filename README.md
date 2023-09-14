# YouTube-Video-Processor
A scalable YouTube video processing pipeline that seamlessly downloads YouTube videos, processes them with FFmpeg, and uploads the refined videos to Cloudinary ( or S3 etc ..). This project uses Celery for distributed task processing and RabbitMQ as a message broker, ensuring an efficient and scalable workflow.

![Python](https://img.shields.io/badge/Python-3.9-blue)
![Docker-Compose](https://img.shields.io/badge/Docker--Compose-3.0-blue)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.8-red)
![Flask](https://img.shields.io/badge/Flask-2.0-green)
![Cloudinary](https://img.shields.io/badge/Cloudinary-1.0-yellow)
![Celery](https://img.shields.io/badge/Celery-5.0-brightgreen)


# Key Features:
- YouTube video downloading using Pytube
- Video processing with FFmpeg for various resolutions
- Uploading processed videos to Cloudinary with detailed logging
- Scalable architecture with Celery and RabbitMQ
- Containerized application setup with Docker and docker-compose
- MongoDB integration for data storage and change streams monitoring

## How to Run and Scale the Project 🚀

### Step 1: Setting Up Environment Variables
Before you start, ensure to configure necessary environment variables in the \`.env\` file. Use the \`.env.example\` as a template to create your \`.env\` file with the appropriate values.

### Step 2: Building and Running the Project
Navigate to the project's root directory and execute the following command:

```docker-compose up --build```

### Step 3: Scaling the Project

Scale the project and increase the processing by initiating more Celery worker instances using the \`--scale\` option:

```docker-compose up --scale celery=3```

### Step 4: Sending API Requests
Once the application is running, you can send POST requests to the endpoint `http://localhost:5000/process_video` to initiate the video processing task.
You can use the following `curl` command as an example to send a request:
```curl -X POST -H "Content-Type: application/json" -d '{"video_url": "https://www.youtube.com/watch?v=RQBqBTUY9Hw","preferred_resolution":"720p"}' http://localhost:5000/process_video```


### Step 5: Monitoring and Managing the Queue
Manage and monitor the message queues by accessing the RabbitMQ management interface at \`http://localhost:15672\` ( Default user and password are "guest").

## Contribution 🤝
Feel free to fork the project, create a feature branch, and send me a pull request.

## License 📄
This project is licensed under the MIT License.

## Contact 📧
For more information, feel free to contact me.


