"""
ai-profanity-filter - Main orchestration module
Detects and censors abusive words from movies using AI transcription and audio processing.
"""

import os
import sys
import argparse
from pathlib import Path

# Import our custom modules
from utils.audio_utils import extract_audio, merge_audio_to_video
from services.transcription import transcribe_with_whisper
from utils.censor_utils import detect_and_censor_audio


def main():
    """Main function to orchestrate the movie censoring pipeline."""
    parser = argparse.ArgumentParser(description='ai-profanity-filter - Censor abusive words from videos')
    parser.add_argument('input_video', help='Path to the input video file')
    parser.add_argument('--output', '-o', help='Output video filename (optional)')
    parser.add_argument('--temp-dir', default='temp', help='Temporary directory for processing files')
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input_video)
    if not input_path.exists():
        print(f"Error: Input video file '{input_path}' not found.")
        sys.exit(1)
    
    # Set up output path
    if args.output:
        output_path = Path('outputs') / args.output
    else:
        output_path = Path('outputs') / f"censored_{input_path.name}"
    
    # Create necessary directories
    temp_dir = Path(args.temp_dir)
    temp_dir.mkdir(exist_ok=True)
    Path('outputs').mkdir(exist_ok=True)
    
    print("🎬 Starting ai-profanity-filter processing...")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    
    try:
        # Step 1: Extract audio from video
        print("\n🔊 Step 1: Extracting audio from video...")
        audio_path = temp_dir / f"{input_path.stem}_audio.wav"
        extract_audio(str(input_path), str(audio_path))
        print(f"✅ Audio extracted to: {audio_path}")
        
        # Step 2: Transcribe audio using Whisper
        print("\n🎙️ Step 2: Transcribing audio with OpenAI Whisper...")
        transcript_data = transcribe_with_whisper(str(audio_path))
        print(f"✅ Transcription completed. Found {len(transcript_data['segments'])} segments.")
        
        # Step 3: Detect abusive words and create censored audio
        print("\n🚫 Step 3: Detecting and censoring abusive words...")
        censored_audio_path = temp_dir / f"{input_path.stem}_censored_audio.wav"
        profane_count = detect_and_censor_audio(
            str(audio_path), 
            transcript_data, 
            str(censored_audio_path),
            censor_type="mute"  # Use silence instead of beep
        )
        print(f"✅ Audio censored. Found and replaced {profane_count} abusive words.")
        
        # Step 4: Merge censored audio back into video
        print("\n🎞️ Step 4: Merging censored audio back into video...")
        merge_audio_to_video(
            str(input_path), 
            str(censored_audio_path), 
            str(output_path)
        )
        print(f"✅ Final censored video saved to: {output_path}")
        
        # Cleanup temporary files
        print("\n🧹 Cleaning up temporary files...")
        if audio_path.exists():
            audio_path.unlink()
        if censored_audio_path.exists():
            censored_audio_path.unlink()
        
        print("\n🎉 ai-profanity-filter processing completed successfully!")
        print(f"📁 Output file: {output_path.absolute()}")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
