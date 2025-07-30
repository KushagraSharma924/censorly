"""
Main video processing orchestrator for AI Profanity Filter
Handles the complete video processing pipeline with modular architecture.
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import our modular components
from modules.transcribe import transcribe_with_whisper
from modules.detect_words import detect_abusive_words
from modules.detect_nsfw import detect_nsfw_scenes
from modules.ffmpeg_tools import (
    extract_audio, merge_audio_to_video, apply_beep, apply_mute, cut_scenes,
    validate_video_file, get_video_duration
)


def process_video(input_path: str, mode: str, temp_dir: Optional[str] = None, 
                 custom_words: Optional[List[str]] = None,
                 nsfw_model: str = "nudenet") -> Dict[str, Any]:
    """
    Main video processing function with modular architecture.
    
    Args:
        input_path (str): Path to the input video file
        mode (str): Processing mode ('beep', 'mute', 'cut-scene', 'cut-nsfw')
        temp_dir (str, optional): Temporary directory for processing files
        custom_words (List[str], optional): Custom profanity words to add
        nsfw_model (str): Model type for NSFW detection
    
    Returns:
        Dict with processing results and output path
    
    Raises:
        Exception: If processing fails at any stage
    """
    try:
        # Validate inputs
        if not validate_video_file(input_path):
            raise Exception(f"Invalid or missing video file: {input_path}")
        
        if mode not in ['beep', 'mute', 'cut-scene', 'cut-nsfw']:
            raise Exception(f"Unsupported mode: {mode}. Use 'beep', 'mute', 'cut-scene', or 'cut-nsfw'")
        
        # Set up directories
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp(prefix="video_processing_")
        
        temp_path = Path(temp_dir)
        temp_path.mkdir(exist_ok=True)
        
        input_file = Path(input_path)
        job_id = str(uuid.uuid4())[:8]
        
        print(f"🎬 Starting video processing with mode: {mode}")
        print(f"📁 Input: {input_path}")
        print(f"🆔 Job ID: {job_id}")
        
        result = {
            'job_id': job_id,
            'input_path': input_path,
            'mode': mode,
            'status': 'processing',
            'steps_completed': [],
            'segments_processed': 0,
            'output_path': None,
            'error': None
        }
        
        # Generate output path
        output_dir = Path("processed")
        output_dir.mkdir(exist_ok=True)
        output_filename = f"{job_id}_{mode}_{input_file.name}"
        output_path = output_dir / output_filename
        
        # Step 1: Extract audio for audio-based processing
        if mode in ['beep', 'mute']:
            print("\n🔊 Step 1: Extracting audio from video...")
            audio_path = temp_path / f"{job_id}_audio.wav"
            extract_audio(str(input_path), str(audio_path))
            result['steps_completed'].append('audio_extraction')
            print(f"✅ Audio extracted to: {audio_path}")
            
            # Step 2: Transcribe audio
            print("\n🎙️ Step 2: Transcribing audio with Whisper...")
            transcript_data = transcribe_with_whisper(str(audio_path))
            result['steps_completed'].append('transcription')
            print(f"✅ Transcription completed. Found {len(transcript_data.get('segments', []))} segments.")
            
            # Step 3: Detect abusive words
            print("\n🚫 Step 3: Detecting abusive words...")
            if custom_words:
                from modules.detect_words import add_custom_profanity_words
                add_custom_profanity_words(custom_words)
            
            profane_segments = detect_abusive_words(transcript_data)
            result['steps_completed'].append('word_detection')
            result['segments_processed'] = len(profane_segments)
            
            if not profane_segments:
                print("✅ No profane words detected. Copying original video.")
                import shutil
                shutil.copy2(input_path, output_path)
            else:
                print(f"🎯 Found {len(profane_segments)} segments to censor")
                for segment in profane_segments:
                    duration = segment['end'] - segment['start']
                    print(f"  - '{segment['text']}' at {segment['start']:.2f}s-{segment['end']:.2f}s ({duration:.2f}s)")
                
                # Step 4: Apply audio censoring
                print(f"\n🔧 Step 4: Applying {mode} censoring...")
                censored_audio_path = temp_path / f"{job_id}_censored_audio.wav"
                
                if mode == 'beep':
                    apply_beep(str(audio_path), profane_segments, str(censored_audio_path))
                elif mode == 'mute':
                    apply_mute(str(audio_path), profane_segments, str(censored_audio_path))
                
                result['steps_completed'].append('audio_censoring')
                
                # Step 5: Merge censored audio back to video
                print("\n🎞️ Step 5: Merging censored audio back to video...")
                merge_audio_to_video(str(input_path), str(censored_audio_path), str(output_path))
                result['steps_completed'].append('video_merge')
        
        elif mode in ['cut-scene', 'cut-nsfw']:
            # Step 1: Detect NSFW scenes
            print(f"\n👁️ Step 1: Detecting NSFW scenes with {nsfw_model}...")
            nsfw_segments = detect_nsfw_scenes(str(input_path), nsfw_model)
            result['steps_completed'].append('nsfw_detection')
            result['segments_processed'] = len(nsfw_segments)
            
            if not nsfw_segments:
                print("✅ No NSFW content detected. Copying original video.")
                import shutil
                shutil.copy2(input_path, output_path)
            else:
                print(f"🎯 Found {len(nsfw_segments)} NSFW segments to cut")
                for segment in nsfw_segments:
                    duration = segment['end'] - segment['start']
                    print(f"  - {segment.get('type', 'NSFW')} at {segment['start']:.2f}s-{segment['end']:.2f}s ({duration:.2f}s)")
                
                # Step 2: Cut scenes
                print(f"\n✂️ Step 2: Cutting scenes from video...")
                cut_scenes(str(input_path), nsfw_segments, str(output_path))
                result['steps_completed'].append('scene_cutting')
        
        # Final result
        result['status'] = 'completed'
        result['output_path'] = str(output_path)
        
        print(f"\n🎉 Processing completed successfully!")
        print(f"📁 Output file: {output_path}")
        print(f"📊 Processed {result['segments_processed']} segments")
        
        # Cleanup temporary files
        print("\n🧹 Cleaning up temporary files...")
        _cleanup_temp_files(temp_path)
        
        return result
        
    except Exception as e:
        error_msg = f"Error during video processing: {str(e)}"
        print(f"\n❌ {error_msg}")
        
        result['status'] = 'failed'
        result['error'] = error_msg
        
        # Cleanup on error
        if 'temp_path' in locals():
            _cleanup_temp_files(temp_path)
        
        raise Exception(error_msg)


def _cleanup_temp_files(temp_path: Path) -> None:
    """
    Clean up temporary files and directories.
    
    Args:
        temp_path: Path to temporary directory
    """
    try:
        import shutil
        if temp_path.exists():
            shutil.rmtree(temp_path)
            print(f"✅ Cleaned up temporary directory: {temp_path}")
    except Exception as e:
        print(f"⚠️ Warning: Could not clean up temporary files: {e}")


def get_supported_modes() -> List[Dict[str, str]]:
    """
    Get list of supported processing modes.
    
    Returns:
        List of mode dictionaries with descriptions
    """
    return [
        {
            'mode': 'beep',
            'description': 'Replace profane words with beep sounds',
            'type': 'audio_processing',
            'ready': True
        },
        {
            'mode': 'mute',
            'description': 'Replace profane words with silence',
            'type': 'audio_processing',
            'ready': True
        },
        {
            'mode': 'cut-scene',
            'description': 'Cut out NSFW scenes from video',
            'type': 'visual_processing',
            'ready': False,  # Will be True when AI models are integrated
            'note': 'Coming soon - requires AI model integration'
        },
        {
            'mode': 'cut-nsfw',
            'description': 'Cut out NSFW content using AI detection',
            'type': 'visual_processing',
            'ready': False,
            'note': 'Coming soon - requires AI model integration'
        }
    ]


def estimate_processing_time(video_path: str, mode: str) -> Dict[str, Any]:
    """
    Estimate processing time based on video duration and mode.
    
    Args:
        video_path: Path to video file
        mode: Processing mode
    
    Returns:
        Dictionary with time estimates
    """
    try:
        duration = get_video_duration(video_path)
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        
        # Rough estimates based on mode
        if mode in ['beep', 'mute']:
            # Transcription is the bottleneck
            estimated_seconds = duration * 0.3  # ~30% of video length
        elif mode in ['cut-scene', 'cut-nsfw']:
            # Visual processing is more intensive
            estimated_seconds = duration * 1.5  # ~150% of video length
        else:
            estimated_seconds = duration * 0.5
        
        return {
            'video_duration': duration,
            'file_size_mb': file_size_mb,
            'estimated_processing_time': estimated_seconds,
            'mode': mode,
            'complexity': 'high' if mode.startswith('cut-') else 'medium'
        }
        
    except Exception as e:
        return {
            'error': f"Could not estimate processing time: {e}",
            'estimated_processing_time': 60  # Default fallback
        }
