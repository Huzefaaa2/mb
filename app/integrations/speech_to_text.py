"""
Azure Speech to Text Integration Module
Handles speech-to-text conversion and audio processing
"""

import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer

# Load environment variables
load_dotenv()

class SpeechToTextService:
    """Manages Azure Speech to Text operations"""
    
    def __init__(self):
        self.api_key = os.getenv("AZURE_SPEECH_KEY")
        self.region = os.getenv("AZURE_SPEECH_REGION", "southeastasia")
        self.config = None
        self.recognizer = None
        self._init_config()
    
    def _init_config(self):
        """Initialize Speech Configuration"""
        try:
            if not self.api_key or self.api_key.startswith("<"):
                print("⚠️  Speech API key not configured")
                return
            
            self.config = SpeechConfig(
                subscription=self.api_key,
                region=self.region
            )
            print("✓ Speech to Text service initialized")
        except Exception as e:
            print(f"✗ Speech service initialization failed: {e}")
    
    def recognize_from_microphone(self):
        """Recognize speech from microphone"""
        try:
            if not self.config:
                print("✗ Speech service not configured")
                return None
            
            audio_config = AudioConfig(use_default_microphone=True)
            recognizer = SpeechRecognizer(
                speech_config=self.config,
                audio_config=audio_config
            )
            
            print("🎤 Listening...")
            result = recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print(f"✓ Recognized: {result.text}")
                return result.text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print("✗ No speech could be recognized")
                return None
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                print(f"✗ Error: {cancellation.reason}: {cancellation.error_details}")
                return None
        except Exception as e:
            print(f"✗ Speech recognition failed: {e}")
            return None
    
    def recognize_from_file(self, audio_file_path):
        """Recognize speech from audio file"""
        try:
            if not self.config:
                print("✗ Speech service not configured")
                return None
            
            if not os.path.exists(audio_file_path):
                print(f"✗ Audio file not found: {audio_file_path}")
                return None
            
            audio_config = AudioConfig(filename=audio_file_path)
            recognizer = SpeechRecognizer(
                speech_config=self.config,
                audio_config=audio_config
            )
            
            print(f"🎵 Processing: {audio_file_path}")
            result = recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print(f"✓ Transcribed: {result.text}")
                return result.text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print("✗ No speech could be recognized")
                return None
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                print(f"✗ Error: {cancellation.reason}: {cancellation.error_details}")
                return None
        except Exception as e:
            print(f"✗ File speech recognition failed: {e}")
            return None
    
    def continuous_recognize_from_microphone(self, callback=None):
        """Continuously recognize speech from microphone"""
        try:
            if not self.config:
                print("✗ Speech service not configured")
                return
            
            audio_config = AudioConfig(use_default_microphone=True)
            recognizer = SpeechRecognizer(
                speech_config=self.config,
                audio_config=audio_config
            )
            
            # Set up event handlers
            def on_recognized(evt):
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    print(f"✓ Recognized: {evt.result.text}")
                    if callback:
                        callback(evt.result.text)
            
            recognizer.recognized.connect(on_recognized)
            recognizer.start_continuous_recognition()
            print("🎤 Continuous recognition started")
            return recognizer
        except Exception as e:
            print(f"✗ Continuous recognition failed: {e}")
            return None

def test_speech_service():
    """Test Speech to Text service"""
    service = SpeechToTextService()
    if service.config:
        print("✓ Speech service is properly configured")
        return True
    return False

if __name__ == "__main__":
    print("🎙️  Testing Azure Speech to Text Service")
    print("=" * 50)
    
    if test_speech_service():
        print("\n✅ Speech to Text integration ready")
    else:
        print("\n⚠️  Speech to Text requires API key configuration")
