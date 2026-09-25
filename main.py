# import time
# import base64
# from urllib.request import Request, urlopen

# import cv2
# import numpy as np

# from fastapi import FastAPI
# from fastapi.responses import HTMLResponse, StreamingResponse


# # ============================================================
# # FASTAPI APP
# # ============================================================

# app = FastAPI(title="CCTV Streaming Server")


# # ============================================================
# # CAMERA CONFIGURATION
# # ============================================================

# CAMERA_IP = "10.126.35.77"
# CAMERA_PORT = 8080

# CAMERA_USERNAME = "hello"
# CAMERA_PASSWORD = "Pratham@123"

# CAMERA_URL = f"http://{CAMERA_IP}:{CAMERA_PORT}/video"


# # ============================================================
# # BASIC AUTHENTICATION
# # ============================================================

# def get_auth_header():
#     """
#     Create HTTP Basic Authentication header.

#     Equivalent to:

#         curl -u "hello:password"
#     """

#     credentials = f"{CAMERA_USERNAME}:{CAMERA_PASSWORD}"

#     encoded_credentials = base64.b64encode(
#         credentials.encode("utf-8")
#     ).decode("ascii")

#     return f"Basic {encoded_credentials}"


# # ============================================================
# # CAMERA FRAME GENERATOR
# # ============================================================

# def camera_frames():

#     while True:

#         try:

#             print(
#                 f"Connecting to camera: "
#                 f"{CAMERA_IP}:{CAMERA_PORT}/video"
#             )

#             # ------------------------------------------------
#             # Create HTTP request
#             # ------------------------------------------------

#             request = Request(
#                 CAMERA_URL,
#                 headers={
#                     "Authorization": get_auth_header(),
#                     "User-Agent": "Mozilla/5.0",
#                     "Cache-Control": "no-cache",
#                 },
#             )

#             # ------------------------------------------------
#             # Connect to camera
#             # ------------------------------------------------

#             with urlopen(
#                 request,
#                 timeout=10
#             ) as stream:

#                 print("Camera connected!")

#                 buffer = b""

#                 # ============================================
#                 # READ MJPEG STREAM
#                 # ============================================

#                 while True:

#                     chunk = stream.read(8192)

#                     if not chunk:
#                         print("Camera stream ended.")
#                         break

#                     buffer += chunk

#                     # ----------------------------------------
#                     # Find JPEG START
#                     # JPEG starts with FF D8
#                     # ----------------------------------------

#                     start = buffer.find(
#                         b"\xff\xd8"
#                     )

#                     if start == -1:
#                         continue

#                     # ----------------------------------------
#                     # Find JPEG END
#                     # JPEG ends with FF D9
#                     # ----------------------------------------

#                     end = buffer.find(
#                         b"\xff\xd9",
#                         start + 2
#                     )

#                     if end == -1:
#                         continue

#                     end += 2

#                     # ----------------------------------------
#                     # Extract complete JPEG
#                     # ----------------------------------------

#                     jpeg = buffer[start:end]

#                     buffer = buffer[end:]

#                     # ----------------------------------------
#                     # JPEG -> NumPy
#                     # ----------------------------------------

#                     frame_array = np.frombuffer(
#                         jpeg,
#                         dtype=np.uint8
#                     )

#                     # ----------------------------------------
#                     # NumPy -> OpenCV frame
#                     # ----------------------------------------

#                     frame = cv2.imdecode(
#                         frame_array,
#                         cv2.IMREAD_COLOR
#                     )

#                     if frame is None:
#                         continue

#                     # ----------------------------------------
#                     # Return OpenCV frame
#                     # ----------------------------------------

#                     yield frame

#         except Exception as error:

#             print(
#                 f"Camera connection error: {error}"
#             )

#             print("Retrying in 2 seconds...")

#             time.sleep(2)


# # ============================================================
# # PROCESS FRAME + CREATE OUTPUT STREAM
# # ============================================================

# def generate():

#     for frame in camera_frames():

#         # ====================================================
#         # AI / COMPUTER VISION PROCESSING WILL GO HERE
#         # ====================================================

#         # Later we will add YOLO here.
#         #
#         # Example:
#         #
#         # results = model(frame)
#         # frame = results[0].plot()
#         #
#         # ====================================================


#         # ====================================================
#         # OPENCV FRAME -> JPEG
#         # ====================================================

#         success, encoded = cv2.imencode(
#             ".jpg",
#             frame,
#             [
#                 cv2.IMWRITE_JPEG_QUALITY,
#                 80
#             ],
#         )

#         if not success:
#             continue

#         frame_bytes = encoded.tobytes()


#         # ====================================================
#         # SEND MJPEG FRAME
#         # ====================================================

#         yield (
#             b"--frame\r\n"
#             b"Content-Type: image/jpeg\r\n"
#             b"Content-Length: "
#             + str(len(frame_bytes)).encode()
#             + b"\r\n\r\n"
#             + frame_bytes
#             + b"\r\n"
#         )


# # ============================================================
# # VIDEO ENDPOINT
# # ============================================================

# @app.get("/video")
# def video():

#     return StreamingResponse(
#         generate(),
#         media_type="multipart/x-mixed-replace; boundary=frame",
#         headers={
#             "Cache-Control": "no-cache",
#             "Pragma": "no-cache",
#         },
#     )


# # ============================================================
# # HOME PAGE
# # ============================================================

# @app.get(
#     "/",
#     response_class=HTMLResponse
# )
# def home():

#     return """
#     <!DOCTYPE html>

#     <html>

#     <head>

#         <meta charset="UTF-8">

#         <title>CCTV Live Feed</title>

#         <style>

#             * {
#                 box-sizing: border-box;
#             }

#             body {

#                 margin: 0;

#                 background: #111;

#                 color: white;

#                 font-family: Arial, sans-serif;

#                 text-align: center;
#             }

#             h1 {

#                 margin: 20px 0;

#             }

#             .status {

#                 margin-bottom: 20px;

#                 color: #00ff88;

#             }

#             .camera {

#                 display: inline-block;

#                 background: #222;

#                 padding: 15px;

#                 border-radius: 12px;

#                 box-shadow:
#                     0 0 20px
#                     rgba(0, 0, 0, 0.5);
#             }

#             img {

#                 display: block;

#                 width: 800px;

#                 max-width: 90vw;

#                 height: auto;

#                 border-radius: 8px;
#             }

#         </style>

#     </head>


#     <body>

#         <h1>
#             CCTV Live Feed
#         </h1>

#         <div class="status">
#             ● LIVE
#         </div>

#         <div class="camera">

#             <img
#                 src="/video"
#                 alt="CCTV Live Feed"
#             >

#         </div>

#     </body>

#     </html>
#     """


# # ============================================================
# # HEALTH CHECK
# # ============================================================

# @app.get("/health")
# def health():

#     return {

#         "status": "ok",

#         "camera":
#             f"{CAMERA_IP}:{CAMERA_PORT}",

#         "camera_url":
#             CAMERA_URL,

#         "stream":
#             "/video"

#     }


# # ============================================================
# # RUN DIRECTLY WITH PYTHON
# # ============================================================

# if __name__ == "__main__":

#     import uvicorn

#     uvicorn.run(
#         app,
#         host="0.0.0.0",
#         port=8001
#     )







import base64
import time
from urllib.request import Request, urlopen
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# SINGLE GLOBAL APP INSTANCE
app = FastAPI(title="AI CCTV Platform", version="0.1.0")

# ============================================================
# ULTRA-LOW LATENCY CORS MIDDLEWARE CONFIGURATION
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,  # Optimized for open public streams
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# ============================================================
# CAMERA HARDWARE CONFIGURATION
# ============================================================
# NOTE: If you still get a timeout, change this IP to match your camera's actual network IP
CAMERA_IP = "192.168.1.9" 
CAMERA_PORT = 8080
CAMERA_USERNAME = "hello"
CAMERA_PASSWORD = "Pratham@123"
CAMERA_URL = f"http://{CAMERA_IP}:{CAMERA_PORT}/video"

# YOUR ACTIVE LIVE CLOUDFLARE TUNNEL URL
CLOUDFLARE_TUNNEL_URL = "https://significant-proud-reflects-lectures.trycloudflare.com/live"

# ============================================================
# CAMERA REGISTRY
# ============================================================
CAMERAS = {
    "cam1": {
        "id": "cam1",
        "name": "Development Camera",
        "status": "online",
        "streams": {
            "webrtc": f"{CLOUDFLARE_TUNNEL_URL}/video",  # Linked to your endpoint
            "hls": "http://127.0.0",
            "rtsp": "rtsp://127.0.0.1:8554/cam1"
        },
        "ai": {
            "enabled": False,
            "models": []
        }
    }
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_auth_header():
    credentials = f"{CAMERA_USERNAME}:{CAMERA_PASSWORD}"
    encoded = base64.b64encode(credentials.encode("utf-8")).decode("ascii")
    return f"Basic {encoded}"

# ============================================================
# ROUTING & ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {
        "service": "AI CCTV Platform",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "live_feed_ui": "/live"
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "AI CCTV Platform",
        "version": "0.1.0",
        "camera_target": f"{CAMERA_IP}:{CAMERA_PORT}"
    }

@app.get("/api/cameras")
def get_cameras():
    return {
        "count": len(CAMERAS),
        "cameras": list(CAMERAS.values())
    }

@app.get("/api/cameras/{camera_id}")
def get_camera(camera_id: str):
    camera = CAMERAS.get(camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@app.get("/api/cameras/{camera_id}/stream")
def get_camera_stream(camera_id: str):
    camera = CAMERAS.get(camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {
        "camera_id": camera_id,
        "streams": camera["streams"]
    }

@app.get("/video")
def video():
    try:
        request = Request(
            CAMERA_URL,
            headers={
                "Authorization": get_auth_header(),
                "User-Agent": "Mozilla/5.0",
                "Cache-Control": "no-cache",
            },
        )
        
        # 10 second timeout limit to avoid hanging the app if camera drops off
        camera = urlopen(request, timeout=10)
        content_type = camera.headers.get("Content-Type")

        def generate():
            try:
                while True:
                    chunk = camera.read(16384)
                    if not chunk:
                        break
                    yield chunk
            except Exception as error:
                print("Stream disconnected or interrupted:", error)
            finally:
                camera.close()

        return StreamingResponse(
            generate(),
            media_type=None,
            headers={
                "Content-Type": content_type,
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as error:
        print(f"Camera connection failed: {error}")
        raise HTTPException(
            status_code=502, 
            detail=f"Could not connect to target camera stream at {CAMERA_URL}. Error: {str(error)}"
        )

@app.get("/live", response_class=HTMLResponse)
def live_ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CCTV Live Feed</title>
        <style>
            body { margin: 0; background: #111; color: white; font-family: Arial, sans-serif; text-align: center; }
            h1 { margin: 20px; font-weight: 500; }
            .status { color: #00ff88; margin-bottom: 15px; font-weight: bold; }
            img { width: 800px; max-width: 95vw; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
        </style>
    </head>
    <body>
        <h1>CCTV Live Feed</h1>
        <div class="status">● LIVE</div>
        <img src="/video" alt="Live Camera Feed Stream">
    </body>
    </html>
    """

# ============================================================
# EXECUTION ENTRYPOINT
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)











# import base64
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import HTMLResponse
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI(title="AI CCTV Production Platform", version="0.1.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # YOUR SYSTEM PARAMETERS
# CAMERA_IP = "10.226.35.77"
# CAMERA_PORT = 8080

# CAMERAS = {
#     "cam1": {
#         "id": "cam1",
#         "name": "Production CCTV Stream",
#         "status": "online",
#         "streams": {
#             "webrtc": "http://127.0.0",
#             "hls": "http://127.0.0",
#             "rtsp": "rtsp://127.0.0.1:8554/cam1"
#         }
#     }
# }

# @app.get("/", response_class=HTMLResponse)
# def home():
#     return """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <meta charset="UTF-8">
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <title>AI CCTV Production Dashboard</title>
#         <style>
#             body { margin: 0; background: #111; color: white; font-family: Arial, sans-serif; text-align: center; }
#             h1 { margin: 20px; font-weight: 300; letter-spacing: 1px; }
#             .status { color: #00ff88; margin-bottom: 15px; font-weight: bold; }
#             .video-container { width: 800px; max-width: 95vw; margin: 0 auto; background: #000; border-radius: 8px; overflow: hidden; border: 2px solid #333; }
#             iframe { width: 100%; height: 450px; border: none; display: block; }
#         </style>
#     </head>
#     <body>
#         <h1>AI CCTV Production Platform</h1>
#         <div class="status">● LIVE WEBRTC DEPLOYMENT</div>
#         <div class="video-container">
#             <!-- Pulls real-time unbuffered frames directly via local WebRTC loops -->
#             <iframe src="http://127.0.0" allow="autoplay; fullscreen"></iframe>
#         </div>
#     </body>
#     </html>
#     """

# @app.get("/health")
# def health():
#     return {"status": "ok", "service": "AI CCTV Production Platform", "camera": f"{CAMERA_IP}:{CAMERA_PORT}"}

# @app.get("/api/cameras")
# def get_cameras():
#     return {"count": len(CAMERAS), "cameras": list(CAMERAS.values())}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001)
