"""
Audio utilities for ai-profanity-filter
Handles audio extraction from video and merging audio back to video using ffmpeg.
"""

import ffmpeg
import os
from pathlib import Path


def extract_audio(video_path, audio_output_path):
    """
    Extract audio from a video file using ffmpeg.
    
    Args:
        video_path (str): Path to the input video file
        audio_output_path (str): Path where the extracted audio will be saved
    
    Raises:
        Exception: If ffmpeg extraction fails
    """
    try:
        # Use ffmpeg to extract audio as WAV format
        stream = ffmpeg.input(video_path)
        audio = stream.audio
        out = ffmpeg.output(audio, audio_output_path, 
                          acodec='pcm_s16le',  # WAV format
                          ac=1,                # Mono channel
                          ar='16000')          # 16kHz sample rate (good for Whisper)
        
        # Run the ffmpeg command, overwrite output if exists
        ffmpeg.run(out, overwrite_output=True, quiet=True)
        
        # Verify the output file was created
        if not os.path.exists(audio_output_path):
            raise Exception(f"Failed to create audio file: {audio_output_path}")
            
    except ffmpeg.Error as e:
        raise Exception(f"FFmpeg error during audio extraction: {e}")
    except Exception as e:
        raise Exception(f"Error extracting audio: {e}")


def merge_audio_to_video(video_path, audio_path, output_path):
    """
    Merge a new audio track with an existing video file using ffmpeg.
    
    Args:
        video_path (str): Path to the original video file
        audio_path (str): Path to the new audio file
        output_path (str): Path where the merged video will be saved
    
    Raises:
        Exception: If ffmpeg merging fails
    """
    try:
        # Load video and audio streams
        video_stream = ffmpeg.input(video_path).video
        audio_stream = ffmpeg.input(audio_path).audio
        
        # Combine video and audio streams
        out = ffmpeg.output(
            video_stream, 
            audio_stream, 
            output_path,
            vcodec='copy',    # Copy video stream without re-encoding
            acodec='aac',     # Encode audio as AAC
            strict='experimental'
        )
        
        # Run the ffmpeg command, overwrite output if exists
        ffmpeg.run(out, overwrite_output=True, quiet=False)
        
        # Verify the output file was created
        if not os.path.exists(output_path):
            raise Exception(f"Failed to create output video: {output_path}")
            
    except ffmpeg.Error as e:
        raise Exception(f"FFmpeg error during audio/video merging: {e}")
    except Exception as e:
        raise Exception(f"Error merging audio to video: {e}")


def get_audio_duration(audio_path):
    """
    Get the duration of an audio file in seconds.
    
    Args:
        audio_path (str): Path to the audio file
    
    Returns:
        float: Duration in seconds
    """
    try:
        probe = ffmpeg.probe(audio_path)
        duration = float(probe['streams'][0]['duration'])
        return duration
    except Exception as e:
        raise Exception(f"Error getting audio duration: {e}")


def validate_video_file(video_path):
    """
    Validate that a video file exists and is readable by ffmpeg.
    
    Args:
        video_path (str): Path to the video file
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if not os.path.exists(video_path):
            return False
        
        # Try to probe the file
        ffmpeg.probe(video_path)
        return True
    except:
        return False
