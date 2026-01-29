# Magic Bus Compass 360 - Main App Package

# Multi-Modal Screening Engine
import sqlite3
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
DB_PATH = Path(__file__).parent.parent / "data" / "mb_compass.db"


class SoftSkillsExtractor:
    """Extracts soft skills from speech transcripts using AI analysis"""
    
    SOFT_SKILLS_KEYWORDS = {
        "communication_confidence": [
            "clear", "articulate", "confident", "fluent", "expressive",
            "engaging", "enthusiastic", "well-spoken", "persuasive", "coherent",
            "communicate", "speak", "presentation"
        ],
        "cultural_fit": [
            "team", "collaborate", "adapt", "flexible", "diverse",
            "inclusive", "respect", "value", "community", "together", "support",
            "cooperation", "teamwork", "team player"
        ],
        "problem_solving": [
            "solve", "approach", "strategy", "solution", "challenge",
            "overcome", "think", "analyze", "improve", "optimize", "handle",
            "problem", "resolve", "critical"
        ],
        "emotional_intelligence": [
            "understand", "empathy", "feel", "care", "concern",
            "listen", "support", "help", "relate", "connect", "appreciate",
            "emotional", "compassion", "sensitivity"
        ],
        "leadership_potential": [
            "lead", "initiative", "responsibility", "motivate", "inspire",
            "guide", "manage", "organize", "coordinate", "delegate", "champion",
            "leadership", "leader", "lead others"
        ]
    }
    
    def analyze_transcript(self, transcript: str) -> Dict[str, float]:
        """Analyze transcript for soft skills using flexible keyword matching"""
        try:
            scores = {}
            transcript_lower = transcript.lower()
            words = transcript.split()
            word_count = len(words)
            
            for skill, keywords in self.SOFT_SKILLS_KEYWORDS.items():
                # Count keyword matches using word boundary matching
                keyword_count = 0
                keyword_weights = {}
                
                import re
                for kw in keywords:
                    pattern = r'\b' + re.escape(kw) + r'\b'
                    match_count = len(re.findall(pattern, transcript_lower))
                    if match_count > 0:
                        keyword_count += min(2, match_count)  # Cap at 2 matches per keyword
                
                # Score calculation:
                # Each keyword match = 10 base points
                # Minimum score if any keyword found = 40
                # Maximum possible = 100
                if keyword_count == 0:
                    keyword_score = 0
                else:
                    keyword_score = min(100, 40 + (keyword_count * 8))
                
                # Adjust based on verbosity (longer transcripts are more reliable)
                if word_count < 30:
                    keyword_score *= 0.75
                elif word_count < 100:
                    keyword_score *= 0.85
                elif word_count > 800:
                    keyword_score *= 0.95
                    
                scores[skill] = round(keyword_score, 1)
            
            # Calculate overall communication score (weighted average)
            scores["overall_communication"] = round(
                scores.get("communication_confidence", 0) * 0.4 +
                scores.get("emotional_intelligence", 0) * 0.3 +
                scores.get("cultural_fit", 0) * 0.3, 1
            )
            
            # Optionally enhance with GPT analysis
            gpt_scores = self.analyze_with_gpt(transcript)
            if gpt_scores:
                # Blend GPT scores (50% weight) with keyword scores (50% weight)
                for skill in scores:
                    if skill in gpt_scores and skill != "overall_communication":
                        scores[skill] = round(scores[skill] * 0.5 + gpt_scores[skill] * 0.5, 1)
                
                # Recalculate overall with blended scores
                scores["overall_communication"] = round(
                    scores.get("communication_confidence", 0) * 0.4 +
                    scores.get("emotional_intelligence", 0) * 0.3 +
                    scores.get("cultural_fit", 0) * 0.3, 1
                )
            
            return scores
        except Exception as e:
            logger.error(f"Error analyzing transcript: {e}")
            return {skill: 0 for skill in self.SOFT_SKILLS_KEYWORDS.keys()}
    
    def analyze_with_gpt(self, transcript: str) -> Optional[Dict[str, float]]:
        """Enhance analysis with GPT-based NLP (optional)"""
        try:
            api_key = os.getenv("AZURE_OPENAI_KEY")
            if not api_key or api_key.startswith("<"):
                return None
            
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=api_key,
                api_version="2024-02-15-preview",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "")
            )
            
            prompt = f"""Analyze this transcript for soft skills and rate on a scale of 0-100:

Transcript: {transcript[:500]}

Rate the following (0-100 each):
1. communication_confidence: How clear, articulate, and engaging is the speaker?
2. cultural_fit: How collaborative and inclusive is the speaker?
3. problem_solving: How analytical and solution-oriented is the speaker?
4. emotional_intelligence: How empathetic and understanding is the speaker?
5. leadership_potential: How much initiative and motivation is shown?

Return ONLY a JSON object like:
{{"communication_confidence": 45, "cultural_fit": 50, "problem_solving": 40, "emotional_intelligence": 55, "leadership_potential": 50}}"""
            
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            # Parse JSON response
            response_text = response.choices[0].message.content
            import json
            scores = json.loads(response_text)
            
            # Normalize to 0-100 range
            return {k: min(100, max(0, v)) for k, v in scores.items()}
        except ImportError:
            logger.warning("Azure OpenAI SDK not installed")
            return None
        except Exception as e:
            logger.warning(f"GPT analysis failed (using keyword only): {e}")
            return None


class AzureSpeechToTextService:
    """Integrates Azure Speech-to-Text for voice transcription"""
    
    def __init__(self):
        self.api_key = os.getenv("AZURE_SPEECH_KEY")
        self.region = os.getenv("AZURE_SPEECH_REGION", "southeastasia")
        self.speech_config = None
        
        if self.api_key and not self.api_key.startswith("<"):
            try:
                import azure.cognitiveservices.speech as speechsdk
                self.speech_config = speechsdk.SpeechConfig(
                    subscription=self.api_key,
                    region=self.region
                )
                logger.info("Azure Speech-to-Text service initialized")
            except ImportError:
                logger.warning("Azure Speech SDK not installed. Install: pip install azure-cognitiveservices-speech")
            except Exception as e:
                logger.warning(f"Azure Speech-to-Text initialization failed: {e}")
    
    def transcribe_audio_file(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio file using Azure Speech-to-Text"""
        try:
            if not self.speech_config:
                logger.warning("Azure Speech-to-Text not configured, skipping transcription")
                return None
            
            import azure.cognitiveservices.speech as speechsdk
            
            # Validate file exists
            if not Path(audio_file_path).exists():
                logger.error(f"Audio file not found: {audio_file_path}")
                return None
            
            # Create recognizer with audio file
            audio_config = speechsdk.AudioConfig(filename=audio_file_path)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            logger.info(f"Transcribing audio file: {audio_file_path}")
            result = recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedFromFile:
                transcript = result.text
                logger.info(f"Transcription successful: {len(transcript)} characters")
                return transcript
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logger.warning("No speech detected in audio file")
                return None
            elif result.reason == speechsdk.ResultReason.Canceled:
                error = result.cancellation_details
                logger.error(f"Speech recognition canceled: {error.reason} - {error.error_details}")
                return None
        except ImportError:
            logger.warning("Azure Speech SDK not available")
            return None
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    def transcribe_from_microphone(self, duration_seconds: int = 30) -> Optional[str]:
        """Transcribe speech from microphone (real-time)"""
        try:
            if not self.speech_config:
                logger.warning("Azure Speech-to-Text not configured")
                return None
            
            import azure.cognitiveservices.speech as speechsdk
            
            audio_config = speechsdk.AudioConfig(use_default_microphone=True)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            logger.info(f"Listening for speech ({duration_seconds}s timeout)...")
            result = recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedFromMic:
                transcript = result.text
                logger.info(f"Microphone transcription: {len(transcript)} characters")
                return transcript
            else:
                logger.warning(f"Microphone recognition failed: {result.reason}")
                return None
        except ImportError:
            logger.warning("Azure Speech SDK not available")
            return None
        except Exception as e:
            logger.error(f"Microphone transcription failed: {e}")
            return None



class MultiModalScreeningService:
    """Complete multi-modal screening pipeline"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self.skills_extractor = SoftSkillsExtractor()
        self.speech_service = AzureSpeechToTextService()
        self._init_db()
    
    def _init_db(self):
        """Initialize screening database table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='mb_multimodal_screenings'
            """)
            
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE mb_multimodal_screenings (
                        screening_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id VARCHAR(50) NOT NULL,
                        submission_type VARCHAR(20) NOT NULL,
                        media_path VARCHAR(500),
                        transcription TEXT,
                        communication_confidence REAL,
                        cultural_fit_score REAL,
                        problem_solving_score REAL,
                        emotional_intelligence REAL,
                        leadership_potential REAL,
                        overall_soft_skill_score REAL,
                        extraction_confidence REAL,
                        top_role_match VARCHAR(100),
                        role_match_confidence REAL,
                        role_recommendations TEXT,
                        personality_fit_level VARCHAR(20),
                        marginalized_score REAL,
                        neet_score REAL,
                        screening_status VARCHAR(20) DEFAULT 'completed',
                        reviewer_notes TEXT,
                        manual_override_score REAL,
                        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        extracted_at TIMESTAMP,
                        scored_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_screening_student 
                    ON mb_multimodal_screenings(student_id)
                """)
                
                conn.commit()
                logger.info("Screening table initialized")
            
            conn.close()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def screen_candidate_voice(self, student_id: int, transcript: str) -> Dict:
        """Screen candidate from voice transcript"""
        try:
            logger.info(f"Screening student {student_id} from voice")
            
            # Extract soft skills
            soft_skills = self.skills_extractor.analyze_transcript(transcript)
            
            # Calculate composite scores
            personality_fit, marginalized_score, recommended_roles = self._calculate_fit_scores(
                soft_skills, student_id
            )
            
            # Overall score (average of the 5 core skills, not including overall_communication)
            core_skills = [v for k, v in soft_skills.items() if k != 'overall_communication']
            overall_score = sum(core_skills) / len(core_skills) if core_skills else 0
            
            screening_result = {
                "student_id": student_id,
                "submission_type": "voice_note",
                "transcription": transcript,
                "communication_confidence": soft_skills.get("communication_confidence", 0),
                "cultural_fit_score": soft_skills.get("cultural_fit", 0),
                "problem_solving_score": soft_skills.get("problem_solving", 0),
                "emotional_intelligence": soft_skills.get("emotional_intelligence", 0),
                "leadership_potential": soft_skills.get("leadership_potential", 0),
                "overall_soft_skill_score": overall_score,
                "extraction_confidence": 85.0,
                "personality_fit_level": personality_fit,
                "marginalized_score": marginalized_score,
                "neet_score": 0,
                "top_role_match": recommended_roles[0] if recommended_roles else "General",
                "role_recommendations": json.dumps(recommended_roles)
            }
            
            self._save_screening(screening_result)
            return screening_result
        except Exception as e:
            logger.error(f"Voice screening failed: {e}")
            return {"error": str(e)}
    
    def screen_candidate_from_audio(self, student_id: int, audio_file_path: str) -> Dict:
        """Screen candidate from audio file (WhatsApp voice note, etc.)"""
        try:
            logger.info(f"Processing audio file for student {student_id}: {audio_file_path}")
            
            # Transcribe audio
            transcript = self.speech_service.transcribe_audio_file(audio_file_path)
            
            if not transcript:
                logger.warning(f"Could not transcribe audio for student {student_id}")
                return {"error": "Audio transcription failed", "student_id": student_id}
            
            logger.info(f"Transcription complete: {len(transcript)} characters")
            
            # Screen using transcript
            result = self.screen_candidate_voice(student_id, transcript)
            
            # Add media path to result
            if "error" not in result:
                result["media_path"] = audio_file_path
                result["submission_type"] = "whatsapp_voice" if "whatsapp" in audio_file_path.lower() else "voice_note"
            
            return result
        except Exception as e:
            logger.error(f"Audio screening failed: {e}")
            return {"error": str(e)}
    
    def _calculate_fit_scores(self, soft_skills: Dict, student_id: int) -> Tuple[str, float, List[str]]:
        """Calculate personality fit scores and recommended roles"""
        try:
            comm = soft_skills.get("communication_confidence", 0)
            cultural = soft_skills.get("cultural_fit", 0)
            ei = soft_skills.get("emotional_intelligence", 0)
            
            personality_score = (comm * 0.4 + cultural * 0.35 + ei * 0.25)
            
            roles = []
            if comm > 35:
                roles.extend(["Customer Service", "Sales", "Team Lead"])
            if cultural > 35:
                roles.extend(["HR", "Community Engagement", "Mentorship"])
            if ei > 35:
                roles.extend(["Support Role", "Counselor", "Coach"])
            
            marginalized_score = personality_score * 1.15
            
            # Fit label based on personality score distribution
            fit_label = (
                "High" if personality_score > 30 else
                "Medium" if personality_score > 15 else
                "Low"
            )
            
            return fit_label, marginalized_score, list(set(roles))
        except Exception as e:
            logger.error(f"Fit calculation failed: {e}")
            return "Unknown", 0, []
    
    def _save_screening(self, result: Dict):
        """Save screening to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO mb_multimodal_screenings (
                    student_id, submission_type, transcription,
                    communication_confidence, cultural_fit_score, problem_solving_score,
                    emotional_intelligence, leadership_potential, overall_soft_skill_score,
                    extraction_confidence, personality_fit_level, marginalized_score,
                    neet_score, top_role_match, role_recommendations,
                    extracted_at, scored_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.get("student_id"),
                result.get("submission_type"),
                result.get("transcription"),
                result.get("communication_confidence"),
                result.get("cultural_fit_score"),
                result.get("problem_solving_score"),
                result.get("emotional_intelligence"),
                result.get("leadership_potential"),
                result.get("overall_soft_skill_score"),
                result.get("extraction_confidence"),
                result.get("personality_fit_level"),
                result.get("marginalized_score"),
                result.get("neet_score"),
                result.get("top_role_match"),
                result.get("role_recommendations"),
                datetime.now(),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Screening saved for student {result.get('student_id')}")
        except Exception as e:
            logger.error(f"Failed to save screening: {e}")
    
    def get_candidate_screenings(self, student_id: int) -> List[Dict]:
        """Get screenings for a candidate"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM mb_multimodal_screenings 
                WHERE student_id = ? 
                ORDER BY created_at DESC
            """, (student_id,))
            
            columns = [desc[0] for desc in cursor.description]
            screenings = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return screenings
        except Exception as e:
            logger.error(f"Failed to retrieve screenings: {e}")
            return []
    
    def get_personality_driven_candidates(self, min_score: float = 70) -> List[Dict]:
        """Get candidates suitable for personality-driven roles"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT 
                    ms.student_id,
                    ms.communication_confidence,
                    ms.cultural_fit_score,
                    ms.overall_soft_skill_score,
                    ms.personality_fit_level,
                    ms.role_recommendations
                FROM mb_multimodal_screenings ms
                WHERE ms.overall_soft_skill_score >= ?
                ORDER BY ms.overall_soft_skill_score DESC
            """, (min_score,))
            
            columns = [desc[0] for desc in cursor.description]
            candidates = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return candidates
        except Exception as e:
            logger.error(f"Failed to get personality-driven candidates: {e}")
            return []
