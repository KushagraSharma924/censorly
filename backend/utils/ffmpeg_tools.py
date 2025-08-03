"""
FFmpeg tools module for AI Profanity Filter
Handles video/audio processing, censoring, and scene cutting using ffmpeg.
"""

import ffmpeg
import os
from pathlib import Path
from pydub import AudioSegment
from pydub.generators import Sine
from typing import List, Dict, Any


def extract_audio(video_path: str, audio_output_path: str) -> None:
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


def merge_audio_to_video(video_path: str, audio_path: str, output_path: str) -> None:
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


def create_beep_sound(duration_ms: int, frequency: int = 1000) -> AudioSegment:
    """
    Create a beep sound of specified duration.
    
    Args:
        duration_ms (int): Duration in milliseconds
        frequency (int): Frequency of the beep in Hz
    
    Returns:
        AudioSegment containing the beep sound
    """
    # Generate sine wave beep
    beep = Sine(frequency).to_audio_segment(duration=duration_ms)
    
    # Apply fade in/out to avoid clicking sounds
    beep = beep.fade_in(10).fade_out(10)
    
    # Reduce volume to 50% to make it less harsh
    beep = beep - 6  # Reduce by 6dB
    
    return beep


def apply_beep(audio_path: str, segments: List[Dict[str, Any]], output_path: str) -> int:
    """
    Apply beep censoring to audio segments.
    
    Args:
        audio_path (str): Path to the original audio file
        segments (List[Dict]): List of segments to censor with start/end times
        output_path (str): Path to save the censored audio
    
    Returns:
        int: Number of segments censored
    """
    try:
        if not segments:
            # Copy original file if no processing needed
            import shutil
            shutil.copy2(audio_path, output_path)
            return 0
        
        print(f"Applying beep censoring to {len(segments)} segments...")
        audio = AudioSegment.from_file(audio_path)
        
        # Apply beep censoring to each segment
        censored_audio = audio
        for segment in segments:
            censored_audio = _censor_audio_segment(
                censored_audio,
                segment['start'],
                segment['end'],
                "beep"
            )
        
        print(f"Exporting beep-censored audio to: {output_path}")
        censored_audio.export(output_path, format="wav")
        
        return len(segments)
        
    except Exception as e:
        raise Exception(f"Error during beep censoring: {e}")


def apply_mute(audio_path: str, segments: List[Dict[str, Any]], output_path: str) -> int:
    """
    Apply mute censoring to audio segments.
    
    Args:
        audio_path (str): Path to the original audio file
        segments (List[Dict]): List of segments to censor with start/end times
        output_path (str): Path to save the censored audio
    
    Returns:
        int: Number of segments censored
    """
    try:
        if not segments:
            # Copy original file if no processing needed
            import shutil
            shutil.copy2(audio_path, output_path)
            return 0
        
        print(f"Applying mute censoring to {len(segments)} segments...")
        audio = AudioSegment.from_file(audio_path)
        
        # Apply mute censoring to each segment
        censored_audio = audio
        for segment in segments:
            censored_audio = _censor_audio_segment(
                censored_audio,
                segment['start'],
                segment['end'],
                "mute"
            )
        
        print(f"Exporting muted audio to: {output_path}")
        censored_audio.export(output_path, format="wav")
        
        return len(segments)
        
    except Exception as e:
        raise Exception(f"Error during mute censoring: {e}")


def cut_scenes(video_path: str, segments_to_remove: List[Dict[str, Any]], output_path: str) -> int:
    """
    Cut out specific scenes from video (for NSFW content removal).
    
    Args:
        video_path (str): Path to the original video file
        segments_to_remove (List[Dict]): List of segments to cut out with start/end times
        output_path (str): Path to save the edited video
    
    Returns:
        int: Number of segments cut
    """
    try:
        if not segments_to_remove:
            # Copy original file if no processing needed
            import shutil
            shutil.copy2(video_path, output_path)
            return 0
        
        print(f"Cutting {len(segments_to_remove)} scenes from video...")
        
        # Sort segments by start time
        segments_to_remove.sort(key=lambda x: x['start'])
        
        # Create list of segments to keep
        input_stream = ffmpeg.input(video_path)
        video_duration = float(ffmpeg.probe(video_path)['format']['duration'])
        
        keep_segments = []
        current_time = 0.0
        
        for segment in segments_to_remove:
            if current_time < segment['start']:
                # Add segment before the cut
                keep_segments.append({
                    'start': current_time,
                    'end': segment['start']
                })
            current_time = max(current_time, segment['end'])
        
        # Add final segment after last cut
        if current_time < video_duration:
            keep_segments.append({
                'start': current_time,
                'end': video_duration
            })
        
        if not keep_segments:
            raise Exception("All content would be removed - cannot create output")
        
        # Create concatenated video using ffmpeg
        _concatenate_video_segments(video_path, keep_segments, output_path)
        
        return len(segments_to_remove)
        
    except Exception as e:
        raise Exception(f"Error during scene cutting: {e}")


def _censor_audio_segment(audio: AudioSegment, start_time: float, end_time: float, 
                         censor_type: str = "mute") -> AudioSegment:
    """
    Censor a specific segment of audio.
    
    Args:
        audio (AudioSegment): Original audio
        start_time (float): Start time in seconds
        end_time (float): End time in seconds
        censor_type (str): Type of censoring - "mute" or "beep"
    
    Returns:
        AudioSegment with censored portion
    """
    # Convert times to milliseconds
    start_ms = int(start_time * 1000)
    end_ms = int(end_time * 1000)
    
    # Ensure we don't go beyond audio bounds
    start_ms = max(0, start_ms)
    end_ms = min(len(audio), end_ms)
    
    if start_ms >= end_ms:
        return audio
    
    # Split audio into before, during, and after segments
    before = audio[:start_ms]
    during = audio[start_ms:end_ms]
    after = audio[end_ms:]
    
    if censor_type == "mute":
        # Replace with silence
        censored_segment = AudioSegment.silent(duration=len(during))
    else:  # beep
        # Replace with beep sound
        censored_segment = create_beep_sound(len(during))
        
        # Match the original audio's properties
        if len(during) > 0:
            censored_segment = censored_segment.set_channels(during.channels)
            censored_segment = censored_segment.set_frame_rate(during.frame_rate)
    
    # Combine all segments
    return before + censored_segment + after


def _concatenate_video_segments(video_path: str, keep_segments: List[Dict[str, Any]], 
                               output_path: str) -> None:
    """
    Concatenate video segments using ffmpeg.
    
    Args:
        video_path (str): Original video path
        keep_segments (List[Dict]): Segments to keep with start/end times
        output_path (str): Output video path
    """
    try:
        # Create temporary segment files
        temp_files = []
        temp_dir = Path("temp_segments")
        temp_dir.mkdir(exist_ok=True)
        
        for i, segment in enumerate(keep_segments):
            temp_file = temp_dir / f"segment_{i}.mp4"
            temp_files.append(str(temp_file))
            
            # Extract each segment
            (
                ffmpeg
                .input(video_path, ss=segment['start'], t=segment['end'] - segment['start'])
                .output(str(temp_file), vcodec='copy', acodec='copy')
                .run(overwrite_output=True, quiet=True)
            )
        
        # Concatenate all segments
        if len(temp_files) == 1:
            # Single segment, just copy
            import shutil
            shutil.copy2(temp_files[0], output_path)
        else:
            # Multiple segments, concatenate
            inputs = [ffmpeg.input(f) for f in temp_files]
            (
                ffmpeg
                .concat(*inputs, v=1, a=1)
                .output(output_path)
                .run(overwrite_output=True, quiet=True)
            )
        
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        temp_dir.rmdir()
        
    except Exception as e:
        raise Exception(f"Error concatenating video segments: {e}")


def get_video_duration(video_path: str) -> float:
    """
    Get the duration of a video file in seconds.
    
    Args:
        video_path (str): Path to the video file
    
    Returns:
        float: Duration in seconds
    """
    try:
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        return duration
    except Exception as e:
        raise Exception(f"Error getting video duration: {e}")


def validate_video_file(video_path: str) -> bool:
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


def apply_beep_to_video(video_path: str, segments: List[Dict[str, Any]], output_path: str) -> int:
    """
    Apply beep censoring to video segments by processing audio and merging back.
    
    Args:
        video_path (str): Path to the input video file
        segments (List[Dict]): List of segments to censor with start/end times
        output_path (str): Path to save the censored video
    
    Returns:
        int: Number of segments censored
    """
    try:
        if not segments:
            # Copy original file if no processing needed
            import shutil
            shutil.copy2(video_path, output_path)
            return 0
        
        print(f"Applying beep censoring to video with {len(segments)} segments...")
        
        # Create temporary files
        temp_dir = Path(output_path).parent
        temp_audio = temp_dir / "temp_audio.wav"
        temp_censored_audio = temp_dir / "temp_censored_audio.wav"
        
        try:
            # Step 1: Extract audio from video
            extract_audio(video_path, str(temp_audio))
            
            # Step 2: Apply beep censoring to audio
            apply_beep(str(temp_audio), segments, str(temp_censored_audio))
            
            # Step 3: Merge censored audio back with video
            merge_audio_to_video(video_path, str(temp_censored_audio), output_path)
            
            print(f"✅ Video with beep censoring saved to: {output_path}")
            return len(segments)
            
        finally:
            # Clean up temporary files
            for temp_file in [temp_audio, temp_censored_audio]:
                if temp_file.exists():
                    temp_file.unlink()
        
    except Exception as e:
        raise Exception(f"Error during video beep censoring: {e}")


def apply_mute_to_video(video_path: str, segments: List[Dict[str, Any]], output_path: str) -> int:
    """
    Apply mute censoring to video segments by processing audio and merging back.
    
    Args:
        video_path (str): Path to the input video file
        segments (List[Dict]): List of segments to censor with start/end times
        output_path (str): Path to save the censored video
    
    Returns:
        int: Number of segments censored
    """
    try:
        if not segments:
            # Copy original file if no processing needed
            import shutil
            shutil.copy2(video_path, output_path)
            return 0
        
        print(f"Applying mute censoring to video with {len(segments)} segments...")
        
        # Create temporary files
        temp_dir = Path(output_path).parent
        temp_audio = temp_dir / "temp_audio.wav"
        temp_censored_audio = temp_dir / "temp_censored_audio.wav"
        
        try:
            # Step 1: Extract audio from video
            extract_audio(video_path, str(temp_audio))
            
            # Step 2: Apply mute censoring to audio
            apply_mute(str(temp_audio), segments, str(temp_censored_audio))
            
            # Step 3: Merge censored audio back with video
            merge_audio_to_video(video_path, str(temp_censored_audio), output_path)
            
            print(f"✅ Video with mute censoring saved to: {output_path}")
            return len(segments)
            
        finally:
            # Clean up temporary files
            for temp_file in [temp_audio, temp_censored_audio]:
                if temp_file.exists():
                    temp_file.unlink()
        
    except Exception as e:
        raise Exception(f"Error during video mute censoring: {e}")
