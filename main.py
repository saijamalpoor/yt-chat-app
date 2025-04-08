from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from pytube import YouTube, exceptions
import google.generativeai as genai
from dotenv import load_dotenv
import os
import logging
import requests
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

class ChatRequest(BaseModel):
    video_id: str
    message: str

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro-latest')  # Correct model name

def get_video_info_direct(video_id: str):
    """Alternative method to get video info using YouTube's oembed API"""
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(oembed_url)
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title", "Unknown Title"),
                "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            }
        return None
    except Exception as e:
        logger.error(f"Error in get_video_info_direct: {str(e)}")
        return None

@app.get("/video-info/{video_id}")
async def get_video_info(video_id: str):
    try:
        logger.debug(f"Attempting to fetch info for video ID: {video_id}")
        
        # Validate video ID
        if not video_id or len(video_id) != 11:
            logger.error(f"Invalid video ID format: {video_id}")
            raise HTTPException(status_code=400, detail="Invalid video ID format")
        
        video_info = None
        try:
            # Try direct method first
            video_info = get_video_info_direct(video_id)
            if video_info:
                logger.debug("Successfully got video info using direct method")
        except Exception as e:
            logger.warning(f"Direct method failed: {str(e)}")
        
        if not video_info:
            try:
                # Fallback to pytube
                yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
                video_info = {
                    "title": yt.title,
                    "thumbnail_url": yt.thumbnail_url
                }
                logger.debug(f"Successfully got video info using pytube: {video_info['title']}")
            except exceptions.VideoUnavailable as e:
                logger.error(f"Video is unavailable: {str(e)}")
                raise HTTPException(status_code=400, detail="Video is unavailable or private")
            except exceptions.AgeRestrictedError as e:
                logger.error(f"Age-restricted video: {str(e)}")
                raise HTTPException(status_code=400, detail="Video is age-restricted")
            except Exception as e:
                logger.error(f"Error creating YouTube object: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Error accessing video: {str(e)}")
        
        # Get transcript
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([t["text"] for t in transcript])
            logger.debug("Successfully retrieved transcript")
        except TranscriptsDisabled:
            logger.warning("Transcripts are disabled for this video")
            transcript = []
            transcript_text = "No transcript available for this video."
        except NoTranscriptFound:
            logger.warning("No transcript found for this video")
            transcript = []
            transcript_text = "No transcript available for this video."
        except Exception as e:
            logger.error(f"Error getting transcript: {str(e)}")
            transcript = []
            transcript_text = "Error retrieving transcript."
        
        return {
            "title": video_info["title"],
            "transcript": transcript,
            "thumbnail": video_info["thumbnail_url"],
            "status": "success"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in get_video_info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@app.post("/chat")
async def chat_with_video(request: ChatRequest = Body(...)):
    try:
        logger.debug(f"Processing chat request for video ID: {request.video_id}")
        
        # Get video transcript
        try:
            transcript = YouTubeTranscriptApi.get_transcript(request.video_id)
            transcript_text = " ".join([t["text"] for t in transcript])
            logger.debug("Successfully retrieved transcript")
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            logger.warning(f"Transcript not available: {str(e)}")
            transcript_text = "No transcript available for this video."
        except Exception as e:
            logger.error(f"Error getting transcript: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Error getting transcript: {str(e)}"
            )
        
        # Create the prompt for Gemini
        prompt = f"""You are a helpful assistant discussing a YouTube video. 
        Here's the video transcript: {transcript_text}
        
        User's question: {request.message}
        
        Please provide a helpful response based on the video content."""
        
        # Generate response using Gemini
        try:
            logger.debug("Sending request to Gemini API")
            response = model.generate_content(prompt)
            
            if not response:
                logger.error("Empty response from Gemini API")
                raise Exception("Empty response from Gemini API")
                
            if not response.text:
                logger.error("No text in Gemini response")
                raise Exception("No text in Gemini response")
                
            logger.debug("Successfully received response from Gemini")
            return {
                "response": response.text,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Gemini API error: {str(e)}"
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in chat_with_video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )