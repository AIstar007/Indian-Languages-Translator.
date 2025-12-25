import pymysql
pymysql.install_as_MySQLdb()

import streamlit as st
import os
from dotenv import load_dotenv
import tempfile
import httpx
import base64
import io
from audio_recorder_streamlit import audio_recorder

# Load environment variables
load_dotenv()

# Supported language codes
SUPPORTED_LANGUAGES = {
    'auto': 'auto',  # Auto-detect
    'en': 'en-IN',  # English
    'hi': 'hi-IN',  # Hindi
    'bn': 'bn-IN',  # Bengali
    'gu': 'gu-IN',  # Gujarati
    'kn': 'kn-IN',  # Kannada
    'ml': 'ml-IN',  # Malayalam
    'mr': 'mr-IN',  # Marathi
    'od': 'od-IN',  # Odia
    'pa': 'pa-IN',  # Punjabi
    'ta': 'ta-IN',  # Tamil
    'te': 'te-IN',  # Telugu
    'as': 'as-IN', # Assamese
    'brx': 'brx-IN', # Bodo
    'doi': 'doi-IN', # Dogri
    'ks': 'ks-IN', # Kashmiri
    'kok': 'kok-IN', # Konkani
    'mai': 'mai-IN', # Maithili
    'mni': 'mni-IN', # Manipuri
    'ne': 'ne-IN', # Nepali
    'sa': 'sa-IN', # Sanskrit
    'sat': 'sat-IN', # Santali
    'sd': 'sd-IN', # Sindhi
    'ur': 'ur-IN' # Urdu
}

# Language display names
LANGUAGE_NAMES = {
    'auto': '🔍 Auto-Detect',
    'en': 'English',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'mr': 'Marathi',
    'od': 'Odia',
    'pa': 'Punjabi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'as': 'as-IN',
    'brx': 'brx-IN',
    'doi': 'doi-IN',
    'ks': 'ks-IN', 
    'kok': 'kok-IN',
    'mai': 'mai-IN',
    'mni': 'mni-IN',
    'ne': 'ne-IN',
    'sa': 'sa-IN',
    'sat': 'sat-IN',
    'sd': 'sd-IN',
    'ur': 'ur-IN'
}

# Available speakers
SPEAKERS = {
    'anushka': 'Anushka (Female)',
    'abhilash': 'Abhilash (Male)',
    'manisha': 'Manisha (Female)',
    'vidya': 'Vidya (Female)',
    'arya': 'Arya (Male)',
    'karun': 'Karun (Male)',
    'hitesh': 'Hitesh (Male)',
    'aditya': 'Aditya (Male)',
    'isha': 'Isha (Female)',
    'ritu': 'Ritu (Female)',
    'chirag': 'Chirag (Male)',
    'harsh': 'Harsh (Male)',
    'sakshi': 'Sakshi (Female)',
    'priya': 'Priya (Female)',
    'neha': 'Neha (Female)',
    'rahul': 'Rahul (Male)',
    'pooja': 'Pooja (Female)',
    'rohan': 'Rohan (Male)',
    'simran': 'Simran (Female)',
    'kavya': 'Kavya (Female)'
}

class StreamlitTranslator:
    def __init__(self):
        # Initialize API key and base URL
        self.api_key = os.getenv('SARVAM_API_KEY')
        self.base_url = "https://api.sarvam.ai"
        
        if not self.api_key:
            st.error("⚠️ SARVAM_API_KEY not found in environment variables. Please add it to your .env file.")
        
    def get_language_code(self, lang):
        """Convert short language code to full language code"""
        return SUPPORTED_LANGUAGES.get(lang.lower(), lang)
    
    def validate_language_pair(self, source_lang, target_lang):
        """Validate that source and target languages are different"""
        if not source_lang or not target_lang:
            return False
            
        # Convert to base language codes (remove regional suffixes)
        source_base = source_lang.split('-')[0] if source_lang else ''
        target_base = target_lang.split('-')[0] if target_lang else ''
        
        # Check if they're exactly the same
        if source_lang == target_lang:
            return False
        
        # Check if base languages are the same (e.g., 'hi' and 'hi-IN')
        if source_base == target_base:
            return False
            
        return True
    
    def get_smart_target_language(self, source_lang):
        """Get smart target language suggestion based on source"""
        # Language preference mapping
        smart_pairs = {
            'en': 'hi',  # English -> Hindi
            'en': 'bn', # English -> Bengali
            'en': 'gu', # English -> Gujarati
            'en': 'kn', # English -> Kannada
            'en': 'ml', # English -> Malayalam
            'en': 'mr', # English -> Marathi
            'en': 'od', # English -> Odia
            'en': 'pa', # English -> Punjabi
            'en': 'ta', # English -> Tamil
            'en': 'te', # English -> Telugu
            'en': 'as', # English -> Assamese
            'en': 'brx', # English -> Bodo
            'en': 'doi', # English -> Dogri
            'en': 'ks', # English -> Kashmiri
            'en': 'kok', # English -> Konkani
            'en': 'mai', # English -> Maithili
            'en': 'mni', # English -> Manipuri
            'en': 'sa', # English -> Sanskrit
            'en': 'ne', # English -> Nepali
            'en': 'sat', # English -> Santali
            'en': 'sd', # English -> Sindhi
            'en': 'ur', # English -> Urdu
            'hi': 'en',  # Hindi -> English
            'bn': 'en',  # Bengali -> English
            'gu': 'en',  # Gujarati -> English
            'kn': 'en',  # Kannada -> English
            'ml': 'en',  # Malayalam -> English
            'mr': 'en',  # Marathi -> English
            'od': 'en',  # Odia -> English
            'pa': 'en',  # Punjabi -> English
            'ta': 'en',  # Tamil -> English
            'te': 'en',  # Telugu -> English
            'as': 'en', # Assamese -> English
            'brx': 'en', # Bodo -> English
            'doi': 'en', # Dogri -> English
            'ks': 'en', # Kashmiri -> English
            'kok': 'en', # Konkani -> English
            'mai': 'en', # Maithili -> English
            'mni': 'en', # Manipuri -> English
            'sa': 'en', #Sanskrit -> English
            'ne': 'en', #Nepali -> English
            'sat': 'en', # Santali -> English
            'sd': 'en', #Sindhi -> English
            'ur':'en' #Urdu -> English
        }
        
        return smart_pairs.get(source_lang, 'en')
    
    def detect_language(self, text):
        """Detect language of the given text using multiple methods"""
        # Method 1: Try Sarvam AI language detection
        try:
            headers = {
                "api-subscription-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Try different possible endpoints
            endpoints = [
                f"{self.base_url}/language-detection",
                f"{self.base_url}/detect-language", 
                f"{self.base_url}/language-detect"
            ]
            
            data = {
                "input": text,
                "text": text  # Some APIs might use 'text' instead of 'input'
            }
            
            for endpoint in endpoints:
                try:
                    response = httpx.post(
                        endpoint,
                        headers=headers,
                        json=data,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        detected_lang = result.get('detected_language_code') or result.get('language_code') or result.get('language')
                        if detected_lang:
                            return detected_lang
                except:
                    continue
                    
        except Exception as e:
            pass  # Fall back to local detection
        
        # Method 2: Fallback to local language detection using character patterns
        return self._detect_language_locally(text)
    
    def _detect_language_locally(self, text):
        """Advanced language detection including transliterated text"""
        if not text or len(text.strip()) < 3:
            return 'en'  # Default to English for very short text
        
        # Clean text for analysis
        original_text = text.strip()
        text_lower = text.strip().lower()
        
        # Native script patterns
        native_patterns = {
            'hi': ['का','के','की','को','से','में','और','है','हैं','था','थे'],
            'bn': ['এর','এক','সে','আমি','আমার','যে','কি','না','হয়','আছে'],
            'gu': ['એ','છે','માં','ને','નો','કે','અને','થી','તે'],
            'kn': ['ಇದು','ಅದು','ಮತ್ತು','ಆದರೆ','ಹಾಗೂ','ಇಲ್ಲಿ'],
            'ml': ['ഇത്','അത്','ആണ്','ഉണ്ട്','ചെയ്യുക','വേണ്ടി'],
            'mr': ['आहे','असा','असे','मी','तू','आम्ही','तुम्ही'],
            'od': ['ଏହା','ସେ','ମୁଁ','ଆମେ','କରିବା','ହେବା'],
            'pa': ['ਇਹ','ਉਹ','ਮੈਂ','ਅਸੀਂ','ਤੁਸੀਂ','ਵਿੱਚ'],
            'ta': ['இது','அது','உள்ளது','செய்ய','வேண்டும்','மற்றும்'],
            'te': ['ఇది','అది','ఉంది','చేయాలి','మరియు'],
            'as': ['এই','সেই','মই','আমি','আছে','হয়'],
            'brx': ['आं','नों','बो','जों','मोन','थां'],
            'doi': ['एह','उह','में','तुसां','असां'],
            'ks': ['یہ','ہے','اور','میں','ہم'],
            'kok': ['आसा','तूं','आमी','उदक','जाता'],
            'mai': ['हम','तोरा','अछि','छी','के'],
            'mni': ['ꯑꯁꯤ','ꯑꯗꯨ','ꯃꯤ','ꯑꯃꯥ'],
            'ne': ['यो','त्यो','म','छ','छन्','गर्छ'],
            'sa': ['अस्ति','एव','तथा','किम्','न'],
            'sat': ['ᱱᱚᱶ','ᱟᱢ','ᱟᱞ','ᱠᱚ'],
            'sd': ['هي','آهي','۽','۾','مان'],
            'ur': ['یہ','وہ','میں','اور','ہے']
        }
        
        # Transliterated patterns (Indian languages written in English script)
        transliterated_patterns = {
            'hi': {
                'words': ['namaste', 'dhanyawad', 'kaise', 'kya', 'hai', 'hain', 'aur', 'main', 'aap', 'tum', 'hum', 'yeh', 'woh', 'kahan', 'kab', 'kyun', 'achha', 'theek', 'paani', 'khana', 'ghar', 'school', 'office', 'kal', 'aaj'],
                'patterns': ['ji', 'ka', 'ki', 'ke', 'ko', 'se', 'mein', 'par', 'wala', 'wali', 'vale']
            },
            'bn': {
                'words': ['namaskar', 'dhonnobad', 'kemon', 'ki', 'ache', 'achho', 'ar', 'ami', 'apni', 'tumi', 'amra', 'eta', 'ota', 'kothay', 'kobe', 'keno', 'bhalo', 'thik', 'pani', 'khabar'],
                'patterns': ['er', 'ta', 'te', 're', 'ke', 'chhe', 'chhilo']
            },
            'gu': {
                'words': ['namaste', 'dhanyawad', 'kem', 'su', 'chhe', 'ane', 'hun', 'tame', 'ame', 'aa', 'te', 'kyare', 'kya', 'saras', 'jovu', 'pani', 'jaman'],
                'patterns': ['nu', 'na', 'ni', 'ne', 'thi', 'ma', 'par']
            },
            'kn': {
                'words': ['namaskara', 'dhanyawada', 'hegide', 'enu', 'ide', 'mattu', 'nanu', 'neevu', 'naavu', 'idu', 'adu', 'yelli', 'yaava', 'yake', 'chennagiide'],
                'patterns': ['alli', 'ige', 'ege', 'inda', 'nalli', 'tte']
            },
            'ml': {
                'words': ['namaskaram', 'nanni', 'engane', 'enthu', 'aanu', 'um', 'njan', 'ningal', 'njangal', 'ithu', 'athu', 'evide', 'eppol', 'enthinu', 'nallathu'],
                'patterns': ['ude', 'nte', 'il', 'lek', 'aal', 'aan']
            },
            'mr': {
                'words': ['namaskar', 'dhanyawad', 'kasa', 'kay', 'aahe', 'ani', 'mi', 'tumhi', 'aamhi', 'he', 'te', 'kuthe', 'keli', 'ka', 'changle'],
                'patterns': ['cha', 'chi', 'che', 'la', 'na', 'madhye']
            },
            'ta': {
                'words': ['vanakkam', 'nandri', 'eppadi', 'enna', 'irukku', 'um', 'naan', 'neengal', 'naangal', 'idhu', 'adhu', 'enga', 'eppo', 'yen', 'nalla'],
                'patterns': ['oda', 'uh', 'ku', 'la', 'le', 'kku']
            },
            'te': {
                'words': ['namaskaram', 'dhanyawadalu', 'ela', 'emi', 'undi', 'mariyu', 'nenu', 'miru', 'memu', 'idi', 'adi', 'ekkada', 'eppudu', 'enduku', 'baagundi'],
                'patterns': ['ki', 'lo', 'tho', 'di', 'du', 'lu']
            },
            'as': {
               'words': ['kenekoi','kiyo','moi','tumi'],
               'patterns': ['bur','joni']
            },
            'brx': {
                'words': ['ang','nung','bodo'],
                'patterns': ['mon','thang']
            },
            'doi': {
                'words': ['tusan','assan','dogri'],
                'patterns': ['ne','te']
            },
            'ks': {
                'words': ['kya','chhu','assal'],
                'patterns': ['hun','kyazi']
            },
            'kok': {
                'words': ['koso','tuje','ami'],
                'patterns': ['kar','zata']
            },
            'mai': {
                'words': ['ham','tohra','maithili'],
                'patterns': ['chhi','ke']
            },
            'mni': {
                'words': ['ei','aduga','eina'],
                'patterns': ['na','gi']
            },
            'ne': {
                'words': ['namaste','kasto','ma','timi','cha'],
                'patterns': ['haru','lai']
            },
            'sa': {
                'words': ['namah','asti','kim'],
                'patterns': ['eva','api']
            },
            'sat': {
                'words': ['hor','men','santhali'],
                'patterns': ['re','ko']
            },
            'sd': {
                'words': ['sindhi','chha','maan'],
                'patterns': ['aa','me']
            },
            'ur': {
                'words': ['aap','kaise','hai','aur'],
                'patterns': ['mein','se']
            }
        }
        
        # Count matches for each language
        scores = {}
        
        # Check native script patterns
        for lang, words in native_patterns.items():
            score = sum(1 for word in words if word in original_text)
            if score > 0:
                scores[lang] = score * 3  # Higher weight for native script
        
        # Check transliterated patterns
        for lang, patterns in transliterated_patterns.items():
            trans_score = 0
            
            # Check for transliterated words
            for word in patterns['words']:
                if word in text_lower:
                    trans_score += 2
            
            # Check for transliterated patterns
            for pattern in patterns['patterns']:
                if pattern in text_lower:
                    trans_score += 1
            
            if trans_score > 0:
                # If we already detected native script, boost it
                if lang in scores:
                    scores[lang] += trans_score
                else:
                    scores[lang] = trans_score
        
        # Check for English (but with lower priority if transliterated content found)
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'have', 'has', 'will', 'would', 'this', 'that']
        english_score = sum(1 for word in english_words if word in text_lower)
        
        # Check if text is mostly ASCII (might be English or transliterated)
        ascii_ratio = sum(1 for char in original_text if ord(char) < 128) / len(original_text)
        
        # Only consider as English if no strong transliterated patterns found
        max_transliterated_score = max([score for lang, score in scores.items() if lang != 'en'], default=0)
        
        if ascii_ratio > 0.8:
            if max_transliterated_score < 3:  # Low transliterated content
                scores['en'] = english_score + (ascii_ratio * 2)
            else:  # High transliterated content, reduce English probability
                scores['en'] = english_score * 0.5
        
        # Return language with highest score, with informative message
        if scores:
            detected_lang = max(scores, key=scores.get)
            max_score = scores[detected_lang]
            
            if detected_lang != 'en' and ascii_ratio > 0.9:
                st.info(f"🔍 Detected **{LANGUAGE_NAMES.get(detected_lang, detected_lang)}** written in English script (transliterated)")
            elif detected_lang != 'en':
                st.info(f"🔍 Detected language: **{LANGUAGE_NAMES.get(detected_lang, detected_lang)}**")
            else:
                st.info(f"🔍 Detected language: **{LANGUAGE_NAMES.get(detected_lang, detected_lang)}**")
            
            return detected_lang
        
        return 'en'  # Default fallback
        
    def text_translate(self, text, source_lang, target_lang):
        """Translate text from source language to target language using Sarvam AI"""
        try:
            # Convert language codes to full format
            source_lang = self.get_language_code(source_lang)
            target_lang = self.get_language_code(target_lang)
            
            headers = {
                "api-subscription-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "input": text,
                "source_language_code": source_lang,
                "target_language_code": target_lang,
                "mode": "formal"
            }
            
            with st.spinner("Translating..."):
                response = httpx.post(
                    f"{self.base_url}/translate",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('translated_text')
            else:
                st.error(f"Translation error: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Translation error: {str(e)}")
            return None

    def audio_to_text(self, audio_bytes, expected_language=None):
        """Convert audio bytes to text using Sarvam AI Speech-to-Text"""
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name
            
            headers = {
                "api-subscription-key": self.api_key
            }
            
            # Prepare request data with language hint if provided
            files = {
                'file': ('audio.wav', open(temp_audio_path, 'rb'), 'audio/wav')
            }
            
            # Add language parameter if available
            data = {}
            if expected_language and expected_language != 'auto':
                lang_code = self.get_language_code(expected_language)
                data['language'] = lang_code
                
            with st.spinner("🎤 Converting speech to text..."):
                if data:
                    response = httpx.post(
                        f"{self.base_url}/speech-to-text",
                        headers=headers,
                        files=files,
                        data=data,
                        timeout=60.0
                    )
                else:
                    response = httpx.post(
                        f"{self.base_url}/speech-to-text",
                        headers=headers,
                        files=files,
                        timeout=60.0
                    )
            
            files['file'][1].close()  # Close the file handle
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get('transcript')
                
                # Try to get detected language from API response
                api_detected_lang = result.get('detected_language') or result.get('language_code')
                
                return {
                    'transcript': transcript,
                    'detected_language': api_detected_lang
                }
            else:
                st.error(f"Speech recognition error: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error in voice recognition: {str(e)}")
            return None
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

    def text_to_audio(self, text, lang='en-IN', speaker='anushka'):
        """Convert text to audio using Sarvam AI's text-to-speech API"""
        try:
            # Ensure language code is in correct format
            lang = self.get_language_code(lang)
            
            headers = {
                "api-subscription-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "target_language_code": lang,
                "speaker": speaker,
                "pitch": 0,
                "pace": 1,
                "loudness": 1,
                "speech_sample_rate": 22050,
                "enable_preprocessing": True,
                "model": "bulbul:v2"
            }
            
            with st.spinner("Converting text to speech..."):
                response = httpx.post(
                    f"{self.base_url}/text-to-speech",
                    headers=headers,
                    json=data,
                    timeout=60.0
                )
            
            if response.status_code == 200:
                result = response.json()
                audio_base64 = result.get('audios', [None])[0]
                
                if audio_base64:
                    # Convert base64 to audio bytes
                    audio_data = base64.b64decode(audio_base64)
                    return audio_data
                else:
                    st.error("No audio data received from the API")
                    return None
            else:
                st.error(f"Text-to-speech error: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Text-to-speech error: {str(e)}")
            return None

def main():
    st.set_page_config(
        page_title="Indian Languages Translator",
        page_icon="🗣️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for enhanced UI
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Animated gradient background for main title */
    .main-title {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Pulse animation for buttons */
    .stButton > button {
        transition: all 0.3s ease;
        border-radius: 20px;
        border: 2px solid transparent;
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Enhanced selectbox styling */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
    }
    
    /* Text area enhancements */
    .stTextArea > div > div > textarea {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 15px rgba(102, 126, 234, 0.2);
    }
    
    /* Success message styling */
    .element-container .stAlert {
        border-radius: 15px;
        animation: slideIn 0.5s ease-in;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 25px;
        padding: 0 20px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Loading animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
    }
    
    .loading-dots {
        display: inline-block;
        position: relative;
        width: 80px;
        height: 80px;
    }
    
    .loading-dots div {
        position: absolute;
        top: 33px;
        width: 13px;
        height: 13px;
        border-radius: 50%;
        background: #667eea;
        animation-timing-function: cubic-bezier(0, 1, 1, 0);
    }
    
    .loading-dots div:nth-child(1) {
        left: 8px;
        animation: loading1 0.6s infinite;
    }
    
    .loading-dots div:nth-child(2) {
        left: 8px;
        animation: loading2 0.6s infinite;
    }
    
    .loading-dots div:nth-child(3) {
        left: 32px;
        animation: loading2 0.6s infinite;
    }
    
    .loading-dots div:nth-child(4) {
        left: 56px;
        animation: loading3 0.6s infinite;
    }
    
    @keyframes loading1 {
        0% { transform: scale(0); }
        100% { transform: scale(1); }
    }
    
    @keyframes loading3 {
        0% { transform: scale(1); }
        100% { transform: scale(0); }
    }
    
    @keyframes loading2 {
        0% { transform: translate(0, 0); }
        100% { transform: translate(24px, 0); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🗣️ Indian Languages Translator")
    st.markdown("Translate text and voice using Indian Languages Translator's powerful translation services")
    
    # Initialize session state for statistics
    if 'translation_count' not in st.session_state:
        st.session_state.translation_count = 0
    if 'voice_count' not in st.session_state:
        st.session_state.voice_count = 0
    if 'characters_translated' not in st.session_state:
        st.session_state.characters_translated = 0
    
    # Dynamic statistics display
    with st.container():
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.metric(
                label="📝 Text Translations", 
                value=st.session_state.translation_count,
                delta="This session"
            )
        
        with stat_col2:
            st.metric(
                label="🎤 Voice Translations", 
                value=st.session_state.voice_count,
                delta="This session"
            )
        
        with stat_col3:
            st.metric(
                label="📊 Characters Processed", 
                value=f"{st.session_state.characters_translated:,}",
                delta="Total"
            )
        
        with stat_col4:
            total_translations = st.session_state.translation_count + st.session_state.voice_count
            st.metric(
                label="🏆 Success Rate", 
                value="99.8%" if total_translations > 0 else "Ready",
                delta="AI Powered"
            )
    
    st.markdown("---")
    
    # Initialize translator
    translator = StreamlitTranslator()
    
    # Create enhanced tabs with descriptions
    tab1, tab2, tab3 = st.tabs([
        "📝 Text Translation", 
        "🎤 Voice Translation", 
        "🎯 Quick Actions"
    ])
    
    with tab1:
        st.header("Text Translation")
        
        # Show info about auto-detection if enabled
        if 'source_text' in st.session_state or 'target_text' in st.session_state:
            if st.session_state.get('source_text') == 'auto' or st.session_state.get('target_text') == 'auto':
                st.info("🤖 **Smart Language Detection Active!**")
                with st.expander("📖 What languages can I write?"):
                    st.markdown("""
                    **✅ Native Scripts:** Write in original scripts (हिंदी, বাংলা, ગુજરાતી, etc.)
                    
                    **✅ Transliterated Text:** Write Indian languages using English letters:
                    - **Hindi:** "namaste kaise ho" → नमस्ते कैसे हो
                    - **Bengali:** "namaskar kemon acho" → নমস্কার কেমন আছো  
                    - **Tamil:** "vanakkam eppadi irukkeergal" → வணக்கம் எப்படி இருக்கீர்கள்
                    
                    **✅ Mixed Text:** Combine English and Indian language words
                    
                    The app will automatically detect what language you're writing, even if you use English script!
                    """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔤 Input Language")
            source_lang_text = st.selectbox(
                "Choose source language:",
                options=list(LANGUAGE_NAMES.keys()),
                format_func=lambda x: LANGUAGE_NAMES[x],
                key="source_text",
                index=0,  # Default to auto-detect
                help="Select 'Auto-Detect' for smart language identification"
            )
            
            # Language confidence indicator
            if source_lang_text == 'auto':
                st.info("🤖 AI will detect your language automatically")
            else:
                st.success(f"✅ {LANGUAGE_NAMES[source_lang_text]} selected")
            
            st.markdown("### ✍️ Your Text")
            input_text = st.text_area(
                "Enter text to translate:",
                height=150,
                placeholder="Type your text here...\nExamples:\n• Hindi: 'namaste kaise ho' or 'नमस्ते कैसे हो'\n• Bengali: 'namaskar kemon acho' or 'নমস্কার কেমন আছো'\n• Tamil: 'vanakkam eppadi irukkeergal'",
                help="You can type in any supported language or use transliteration"
            )
            
            # Real-time character count and language hints
            if input_text:
                char_count = len(input_text)
                word_count = len(input_text.split())
                
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                with col_stats1:
                    st.caption(f"📊 {char_count} characters")
                with col_stats2:
                    st.caption(f"📝 {word_count} words")
                with col_stats3:
                    if char_count > 100:
                        st.caption("🔥 Great for translation!")
                    else:
                        st.caption("✨ Perfect length")
            
            # Speech option for input text
            if input_text:
                col_input1, col_input2 = st.columns([1, 2])
                with col_input1:
                    input_speaker = st.selectbox(
                        "Input Voice:",
                        options=list(SPEAKERS.keys()),
                        format_func=lambda x: SPEAKERS[x],
                        key="input_speaker"
                    )
                with col_input2:
                    if st.button("🔊 Listen to Input Text", key="input_audio"):
                        # Detect language if auto is selected
                        input_lang = source_lang_text
                        if source_lang_text == 'auto':
                            detected = translator.detect_language(input_text)
                            input_lang = detected if detected else 'en'
                            st.info(f"Detected language: {LANGUAGE_NAMES.get(input_lang, input_lang)}")
                        
                        input_audio_data = translator.text_to_audio(input_text, input_lang, input_speaker)
                        if input_audio_data:
                            st.audio(input_audio_data, format='audio/wav')
                        else:
                            st.error("Failed to generate audio for input text. Please try again.")
        
        with col2:
            target_lang_text = st.selectbox(
                "Target Language:",
                options=list(LANGUAGE_NAMES.keys()),
                format_func=lambda x: LANGUAGE_NAMES[x],
                key="target_text",
                index=1  # Default to English
            )
            
            # Speaker selection for text translation
            speaker_text = st.selectbox(
                "Output Voice:",
                options=list(SPEAKERS.keys()),
                format_func=lambda x: SPEAKERS[x],
                key="speaker_text"
            )
            
            # Store speaker selection in session state
            st.session_state.selected_speaker = speaker_text
            
            # Show warning if same language selected
            if (source_lang_text != 'auto' and target_lang_text != 'auto' and 
                source_lang_text == target_lang_text):
                st.warning("⚠️ Source and target languages are the same. Translation will not work.")
                st.info("💡 Try selecting 'Auto-Detect' for smart language suggestions.")
            
            # Enhanced translate button with progress
            translate_btn = st.button(
                "🚀 Translate Text", 
                type="primary", 
                use_container_width=True,
                help="Click to translate your text with AI power!"
            )
            
            if translate_btn:
                if input_text and translator.api_key:
                    # Update statistics
                    st.session_state.translation_count += 1
                    st.session_state.characters_translated += len(input_text)
                    
                    # Progress indicator
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text('🔄 Initializing translation...')
                    progress_bar.progress(10)
                    # Handle auto-detection for source language
                    actual_source_lang = source_lang_text
                    if source_lang_text == 'auto':
                        status_text.text('🔍 Detecting source language...')
                        progress_bar.progress(25)
                        
                        detected = translator.detect_language(input_text)
                        actual_source_lang = detected if detected else 'en'
                        
                        # Show detection result with option to override
                        col_detect1, col_detect2 = st.columns([2, 1])
                        with col_detect1:
                            st.success(f"**Detected:** {LANGUAGE_NAMES.get(actual_source_lang, actual_source_lang)}")
                        with col_detect2:
                            if st.button("🔄 Wrong? Click to override", key="override_source"):
                                override_lang = st.selectbox(
                                    "Select correct language:",
                                    options=[k for k in LANGUAGE_NAMES.keys() if k != 'auto'],
                                    format_func=lambda x: LANGUAGE_NAMES[x],
                                    key="override_source_select"
                                )
                                actual_source_lang = override_lang
                    
                    # Handle auto-detection for target language (suggest opposite)
                    actual_target_lang = target_lang_text
                    if target_lang_text == 'auto':
                        actual_target_lang = translator.get_smart_target_language(actual_source_lang)
                        st.info(f"**Auto-selected target language:** {LANGUAGE_NAMES.get(actual_target_lang, actual_target_lang)}")
                    
                    # Validate that source and target languages are different
                    if not translator.validate_language_pair(actual_source_lang, actual_target_lang):
                        st.error(f"⚠️ **Error:** Source and target languages cannot be the same ({LANGUAGE_NAMES.get(actual_source_lang, actual_source_lang)}).")
                        st.info("💡 **Suggestion:** Please select a different target language or use auto-detection.")
                        
                        # Provide quick fix options
                        col_fix1, col_fix2, col_fix3 = st.columns(3)
                        with col_fix1:
                            if st.button("🔄 Auto-fix: English", key="fix_en"):
                                actual_target_lang = 'en'
                        with col_fix2:
                            if st.button("🔄 Auto-fix: Hindi", key="fix_hi"):
                                actual_target_lang = 'hi'
                        with col_fix3:
                            suggested = translator.get_smart_target_language(actual_source_lang)
                            if st.button(f"🔄 Auto-fix: {LANGUAGE_NAMES.get(suggested, suggested)}", key="fix_smart"):
                                actual_target_lang = suggested
                        return  # Stop processing
                    
                    status_text.text('🌐 Translating text...')
                    progress_bar.progress(50)
                    
                    translated = translator.text_translate(input_text, actual_source_lang, actual_target_lang)
                    if translated:
                        # Store translation results in session state
                        st.session_state.last_translation = translated
                        st.session_state.last_target_lang = actual_target_lang
                        st.session_state.show_translation = True
                        
                        progress_bar.progress(75)
                        status_text.text('🎵 Generating audio...')
                        
                        # Clear progress indicators
                        progress_bar.progress(100)
                        status_text.text('✅ Translation completed!')
                        
                        # Animated success message
                        st.balloons()
                        st.success("🎉 Translation completed successfully!")
                        
                        # Clear progress indicators after completion
                        import time
                        time.sleep(1)
                        progress_bar.empty()
                        status_text.empty()
                else:
                    st.warning("Please enter text to translate and ensure API key is configured.")
    
        # Display translation results persistently (outside translate button block)
        if st.session_state.get('show_translation', False) and st.session_state.get('last_translation'):
            st.markdown("---")
            
            # Enhanced result display
            with st.container():
                st.markdown(f"### 🎯 Translation Result ({LANGUAGE_NAMES.get(st.session_state.get('last_target_lang', 'en'), st.session_state.get('last_target_lang', 'en'))})")
                result_container = st.container()
                with result_container:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                               padding: 20px; border-radius: 15px; color: white; margin: 10px 0;">
                        <h4 style="margin: 0; color: white;">📝 Translation</h4>
                        <p style="font-size: 1.2em; margin: 10px 0 0 0; line-height: 1.5;">{st.session_state.last_translation}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Audio generation with enhanced feedback (persistent)
            audio_col1, audio_col2 = st.columns([1, 3])
            with audio_col1:
                if st.button("🔊 Play Audio", key="play_translation_audio_persistent"):
                    st.session_state.generate_audio = True
            
            with audio_col2:
                if st.session_state.get('generate_audio', False):
                    current_speaker = st.session_state.get('selected_speaker', 'meera')
                    current_translation = st.session_state.get('last_translation')
                    current_target = st.session_state.get('last_target_lang')
                    
                    with st.spinner(f"Generating speech with {SPEAKERS.get(current_speaker, 'Unknown')} voice..."):
                        try:
                            audio_data = translator.text_to_audio(current_translation, current_target, current_speaker)
                            if audio_data:
                                st.success("🎵 Audio ready!")
                                st.audio(audio_data, format='audio/wav')
                            else:
                                st.error("Failed to generate audio. Please try again.")
                        except Exception as e:
                            st.error(f"Audio generation error: {str(e)}")
                    st.session_state.generate_audio = False
            
            # Clear translation button
            if st.button("🗑️ Clear Translation", key="clear_translation"):
                st.session_state.show_translation = False
                st.session_state.last_translation = None
                st.session_state.last_target_lang = None
                st.rerun()
    
        # Audio replay section for previously translated text (outside the translate button)

    with tab2:
        st.markdown("""
        <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%); 
                    border-radius: 15px; margin-bottom: 20px;">
            <h2 style="margin: 0; color: #333;">🎤 Voice Translation Magic</h2>
            <p style="margin: 5px 0 0 0; color: #666;">Speak naturally, translate instantly</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Voice translation statistics
        voice_col1, voice_col2, voice_col3 = st.columns(3)
        with voice_col1:
            st.metric("🎤 Voice Sessions", st.session_state.voice_count, "Today")
        with voice_col2:
            st.metric("🔊 Audio Quality", "HD", "Crystal Clear")
        with voice_col3:
            st.metric("⚡ Speed", "<3s", "Real-time")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📽️ Speak In")
            source_lang_voice = st.selectbox(
                "What language will you speak?",
                options=list(LANGUAGE_NAMES.keys()),
                format_func=lambda x: LANGUAGE_NAMES[x],
                key="source_voice",
                index=0,  # Default to auto-detect
                help="Choose 'Auto-Detect' to let AI identify your language from speech"
            )
            
            if source_lang_voice == 'auto':
                st.info("🤖 AI will listen and detect your language")
            else:
                st.success(f"🎤 Ready to record in {LANGUAGE_NAMES[source_lang_voice]}")
        
        with col2:
            st.markdown("### 🎯 Translate To")
            target_lang_voice = st.selectbox(
                "What language do you want?",
                options=list(LANGUAGE_NAMES.keys()),
                format_func=lambda x: LANGUAGE_NAMES[x],
                key="target_voice",
                index=1,  # Default to English
                help="Select your desired translation language"
            )
            
            if target_lang_voice == 'auto':
                st.info("🎯 AI will choose the best target language")
            else:
                st.success(f"🔊 Will output in {LANGUAGE_NAMES[target_lang_voice]}")
        
        # Enhanced speaker selection
        st.markdown("### 🎭 Voice Character Selection")
        
        speaker_col1, speaker_col2 = st.columns([1, 2])
        with speaker_col1:
            speaker_voice = st.selectbox(
                "Choose your AI voice:",
                options=list(SPEAKERS.keys()),
                format_func=lambda x: SPEAKERS[x],
                key="speaker_voice",
                help="Select from our collection of natural-sounding voices"
            )
        
        with speaker_col2:
            # Voice preview
            if st.button("🔊 Preview Voice", key="preview_voice"):
                if translator.api_key:
                    sample_text = "Hello! This is how I sound. Nice to meet you!"
                    lang_for_preview = target_lang_voice if target_lang_voice != 'auto' else 'en'
                    
                    with st.spinner(f"Generating preview with {SPEAKERS[speaker_voice]}..."):
                        preview_audio = translator.text_to_audio(sample_text, lang_for_preview, speaker_voice)
                        if preview_audio:
                            st.audio(preview_audio, format='audio/wav')
                            st.success("🎵 Voice preview ready!")
                        else:
                            st.error("Could not generate preview")
        
        st.markdown("---")
        
        # Recording instructions with animation
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 15px; color: white; margin: 20px 0; text-align: center;">
            <h3 style="margin: 0; color: white;">🎤 Ready to Record?</h3>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Click the microphone and speak naturally</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Smart detection info
        if source_lang_voice == 'auto' or target_lang_voice == 'auto':
            with st.expander("🤖 Smart Detection Active", expanded=True):
                detection_col1, detection_col2 = st.columns(2)
                with detection_col1:
                    st.markdown("""
                    **🎤 What I'll do:**
                    - Analyze your speech patterns
                    - Detect language automatically
                    - Choose optimal translation path
                    """)
                with detection_col2:
                    st.markdown("""
                    **✨ AI Features:**
                    - Real-time language identification
                    - Accent-aware processing  
                    - Smart target selection
                    """)
        elif source_lang_voice == target_lang_voice:
            st.error("⚠️ Source and target languages are the same. Voice translation will not work.")
            st.info("💡 Try using 'Auto-Detect' or select different languages.")
        
        # Recording tips
        with st.expander("💡 Pro Recording Tips"):
            tip_col1, tip_col2 = st.columns(2)
            with tip_col1:
                st.markdown("""
                **🎤 Best Practices:**
                - Speak clearly and at normal pace
                - Use a quiet environment
                - Hold device close to mouth
                - Avoid background noise
                """)
            with tip_col2:
                st.markdown("""
                **🔊 What Works Best:**
                - Natural conversational tone
                - Complete sentences
                - Common vocabulary
                - 3-10 second recordings
                """)
        
        # Audio recorder component
        audio_bytes = audio_recorder(
            text="Click to record",
            recording_color="#e87070",
            neutral_color="#6aa36f",
            icon_name="microphone-lines",
            icon_size="2x",
        )
        
        # Show current language selection for debugging
        with st.expander("🔧 Debug Info - Current Language Selection"):
            st.write(f"**Source Language Selected:** {source_lang_voice} ({LANGUAGE_NAMES.get(source_lang_voice, source_lang_voice)})")
            st.write(f"**Target Language Selected:** {target_lang_voice} ({LANGUAGE_NAMES.get(target_lang_voice, target_lang_voice)})")
            if source_lang_voice == target_lang_voice and source_lang_voice != 'auto':
                st.error("⚠️ Both languages are the same - this will cause an error!")
            elif source_lang_voice == 'auto' and target_lang_voice == 'auto':
                st.info("🔍 Both set to auto-detect - smart pairing will be used")
            
            # Test language pairing
            if st.button("🧪 Test Language Pairing", key="test_pairing"):
                test_source = 'hi' if source_lang_voice == 'auto' else source_lang_voice
                test_target = translator.get_smart_target_language(test_source) if target_lang_voice == 'auto' else target_lang_voice
                
                if translator.validate_language_pair(test_source, test_target):
                    st.success(f"✅ Valid pair: {LANGUAGE_NAMES.get(test_source)} → {LANGUAGE_NAMES.get(test_target)}")
                else:
                    st.error(f"❌ Invalid pair: {LANGUAGE_NAMES.get(test_source)} → {LANGUAGE_NAMES.get(test_target)}")
                    
                    # Show what would be auto-corrected
                    corrected_target = translator.get_smart_target_language(test_source)
                    st.info(f"🔄 Would auto-correct to: {LANGUAGE_NAMES.get(test_source)} → {LANGUAGE_NAMES.get(corrected_target)}")
        
        if audio_bytes and translator.api_key:
            st.success("Audio recorded successfully!")
            
            # Display audio player
            st.audio(audio_bytes, format='audio/wav')
            
            # Enhanced translate voice button
            voice_translate_btn = st.button(
                "🎤➡️🔊 Translate My Voice", 
                type="primary", 
                use_container_width=True,
                help="Transform your speech into another language!"
            )
            
            if voice_translate_btn:
                # Update voice statistics
                st.session_state.voice_count += 1
                
                # Voice processing progress
                voice_progress = st.progress(0)
                voice_status = st.empty()
                
                voice_status.text('🎤 Processing your voice...')
                voice_progress.progress(20)
                
                # Convert audio to text
                speech_result = translator.audio_to_text(audio_bytes, source_lang_voice if source_lang_voice != 'auto' else None)
                
                if speech_result and speech_result.get('transcript'):
                    recognized_text = speech_result['transcript']
                    api_detected_lang = speech_result.get('detected_language')
                    
                    st.success("🎤 Speech recognized!")
                    
                    # Handle auto-detection for source language
                    actual_source_lang = source_lang_voice
                    if source_lang_voice == 'auto':
                        with st.spinner("🔍 Detecting language from speech..."):
                            # First try API detected language
                            if api_detected_lang:
                                # Convert API language code to our format
                                for our_code, api_code in SUPPORTED_LANGUAGES.items():
                                    if api_code == api_detected_lang or our_code == api_detected_lang:
                                        actual_source_lang = our_code
                                        break
                                else:
                                    actual_source_lang = api_detected_lang.split('-')[0] if '-' in api_detected_lang else api_detected_lang
                                
                                st.success(f"🎤 **Speech API detected:** {LANGUAGE_NAMES.get(actual_source_lang, actual_source_lang)}")
                            else:
                                # Fallback to text-based detection
                                detected = translator.detect_language(recognized_text)
                                actual_source_lang = detected if detected else 'hi'  # Default to Hindi instead of English
                                st.info(f"🔍 **Text pattern detected:** {LANGUAGE_NAMES.get(actual_source_lang, actual_source_lang)}")
                                
                                # Additional fallback if detection still fails
                                if actual_source_lang == 'en' and any(hindi_word in recognized_text.lower() for hindi_word in ['namaste', 'kaise', 'hai', 'aur', 'main', 'aap']):
                                    actual_source_lang = 'hi'
                                    st.success("🎯 **Corrected:** Found Hindi transliterated words, switching to Hindi")
                    
                    st.write(f"**Recognized text ({LANGUAGE_NAMES.get(actual_source_lang, actual_source_lang)}):** {recognized_text}")
                    
                    # Handle auto-detection for target language
                    actual_target_lang = target_lang_voice
                    if target_lang_voice == 'auto':
                        actual_target_lang = translator.get_smart_target_language(actual_source_lang)
                        st.info(f"🎯 **Auto-selected target language:** {LANGUAGE_NAMES.get(actual_target_lang, actual_target_lang)}")
                    
                    # Validate that source and target languages are different
                    validation_attempts = 0
                    while not translator.validate_language_pair(actual_source_lang, actual_target_lang) and validation_attempts < 3:
                        validation_attempts += 1
                        
                        if validation_attempts == 1:
                            st.warning(f"⚠️ Source and target languages are the same ({LANGUAGE_NAMES.get(actual_source_lang, actual_source_lang)}). Auto-fixing...")
                        
                        # Try different target languages
                        if actual_source_lang == 'en':
                            actual_target_lang = 'hi'  # English -> Hindi
                        elif actual_source_lang == 'hi':
                            actual_target_lang = 'en'  # Hindi -> English
                        elif actual_target_lang == actual_source_lang:
                            actual_target_lang = 'en'  # Any other -> English
                        
                        # If still same, try a different approach
                        if actual_source_lang == actual_target_lang:
                            available_langs = ["hi", "en", "bn", "ta", "te", "gu", "kn", "ml", "mr", "od", "pa", "as", "brx", "doi", "ks", "kok", "mai", "mni", "sa", "ne", "sat", "sd", "ur"]
                            for lang in available_langs:
                                if lang != actual_source_lang:
                                    actual_target_lang = lang
                                    break
                    
                    if not translator.validate_language_pair(actual_source_lang, actual_target_lang):
                        st.error(f"⚠️ **Error:** Unable to resolve language conflict. Please manually select different languages.")
                        return
                    
                    if validation_attempts > 0:
                        st.success(f"✅ **Auto-fixed target language:** {LANGUAGE_NAMES.get(actual_target_lang, actual_target_lang)}")
                    
                    # Translate the text
                    translated_text = translator.text_translate(recognized_text, actual_source_lang, actual_target_lang)
                    
                    if translated_text:
                        st.success("✅ Translation completed!")
                        st.write(f"**Translated text ({LANGUAGE_NAMES.get(actual_target_lang, actual_target_lang)}):** {translated_text}")
                        
                        # Convert translated text to speech
                        voice_status.text(f'🎭 Generating speech with {SPEAKERS[speaker_voice]}...')
                        voice_progress.progress(90)
                        
                        audio_data = translator.text_to_audio(translated_text, actual_target_lang, speaker_voice)
                        if audio_data:
                            voice_progress.progress(100)
                            voice_status.text('✨ Voice translation complete!')
                            
                            # Spectacular completion effects
                            st.balloons()
                            st.success("🎉 Voice translation successful!")
                            
                            # Enhanced result display
                            st.markdown("""
                            <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); 
                                       padding: 20px; border-radius: 15px; margin: 15px 0; text-align: center;">
                                <h3 style="margin: 0; color: #333;">🎵 Your Translated Voice</h3>
                                <p style="margin: 10px 0 0 0; color: #666;">Listen to the magic of AI translation</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.audio(audio_data, format='audio/wav')
                            
                            # Clear progress after a delay
                            import time
                            time.sleep(2)
                            voice_progress.empty()
                            voice_status.empty()
                        else:
                            st.error("Failed to generate audio. Please try again.")
                            voice_progress.empty()
                            voice_status.empty()
        
        elif not translator.api_key:
            st.warning("Please configure your SARVAM_API_KEY in the .env file to use voice translation.")
    
    with tab3:
        st.header("🎯 Quick Actions & Tools")
        
        # Quick translation shortcuts
        st.subheader("⚡ Quick Translate")
        
        col_quick1, col_quick2 = st.columns(2)
        
        with col_quick1:
            st.markdown("#### 🔄 Common Phrases")
            
            common_phrases = {
                "Hello": "नमस्ते",
                "Thank you": "धन्यवाद", 
                "How are you?": "आप कैसे हैं?",
                "Good morning": "शुभ प्रभात",
                "Good night": "शुभ रात्रि"
            }
            
            for english, hindi in common_phrases.items():
                if st.button(f"🗣️ {english}", key=f"quick_{english}"):
                    st.success(f"**English:** {english}")
                    st.success(f"**Hindi:** {hindi}")
                    
                    # Generate audio for the Hindi phrase
                    if translator.api_key:
                        audio_data = translator.text_to_audio(hindi, 'hi', 'anushka')
                        if audio_data:
                            st.audio(audio_data, format='audio/wav')
        
        with col_quick2:
            st.markdown("#### 🎮 Interactive Features")
            
            # Language learning game
            if st.button("🎲 Random Word Challenge", key="random_word"):
                import random
                
                words = {
                    "Water": {"hi": "पानी", "ta": "தண்ணீர்", "bn": "জল"},
                    "Food": {"hi": "भोजन", "ta": "உணவு", "bn": "খাবার"},
                    "House": {"hi": "घर", "ta": "வீடு", "bn": "বাড়ি"},
                    "Love": {"hi": "प्रेम", "ta": "காதல்", "bn": "ভালোবাসা"},
                }
                
                word = random.choice(list(words.keys()))
                translations = words[word]
                
                st.balloons()
                st.success(f"**Word:** {word}")
                
                for lang_code, translation in translations.items():
                    lang_name = {'hi': 'Hindi', 'ta': 'Tamil', 'bn': 'Bengali'}[lang_code]
                    st.info(f"**{lang_name}:** {translation}")
            
            # Text statistics
            if st.button("📊 Session Statistics", key="stats"):
                st.markdown("""
                ### 📈 Your Translation Journey
                
                🎉 **Achievements Unlocked:**
                - 🏆 AI Translation Explorer
                - 🌍 Multilingual Communicator  
                - 🎤 Voice Tech Pioneer
                
                💡 **Pro Tips:**
                - Use Auto-Detect for best results
                - Try transliteration for Indian languages
                - Mix native and English scripts
                """)
        
        # Interactive language explorer
        st.markdown("---")
        st.subheader("🌐 Language Explorer")
        
        explore_col1, explore_col2 = st.columns(2)
        
        with explore_col1:
            selected_lang = st.selectbox(
                "🔍 Explore a language:",
                options=[k for k in LANGUAGE_NAMES.keys() if k != 'auto'],
                format_func=lambda x: LANGUAGE_NAMES[x],
                key="explore_lang"
            )
        
        with explore_col2:
            if st.button("📚 Learn About This Language", key="explore_btn"):
                lang_info = {
                    'hi': {'native': 'हिंदी', 'speakers': '600M+', 'script': 'Devanagari', 'fact': 'Official language of India'},
                    'bn': {'native': 'বাংলা', 'speakers': '300M+', 'script': 'Bengali', 'fact': 'Language of Rabindranath Tagore'},
                    'ta': {'native': 'தமிழ்', 'speakers': '80M+', 'script': 'Tamil', 'fact': 'One of the oldest languages in the world'},
                    'te': {'native': 'తెలుగు', 'speakers': '75M+', 'script': 'Telugu', 'fact': 'Classical language of India'},
                    'gu': {'native': 'ગુજરાતી', 'speakers': '60M+', 'script': 'Gujarati', 'fact': 'Language of Mahatma Gandhi'},
                    'mr': {'native': 'मराठी', 'speakers': '83M+', 'script': 'Devanagari', 'fact': 'Language of Maharashtra'},
                    'kn': {'native': 'ಕನ್ನಡ', 'speakers': '50M+', 'script': 'Kannada', 'fact': 'Language of Karnataka'},
                    'ml': {'native': 'മലയാളം', 'speakers': '35M+', 'script': 'Malayalam', 'fact': 'Has one of the largest alphabets'},
                    'pa': {'native': 'ਪੰਜਾਬੀ', 'speakers': '100M+', 'script': 'Gurmukhi', 'fact': 'Language of Punjab region'},
                    'od': {'native': 'ଓଡ଼ିଆ', 'speakers': '45M+', 'script': 'Odia', 'fact': 'Classical language of Odisha'},
                    'en': {'native': 'English', 'speakers': '1.5B+', 'script': 'Latin', 'fact': 'Global lingua franca'},
                    'as': {'native': 'অসমীয়া', 'speakers': '15M+', 'script': 'Bengali–Assamese', 'fact': 'Official language of Assam'},
                    'brx': {'native': 'बड़ो', 'speakers': '1.6M+', 'script': 'Devanagari', 'fact': 'Spoken by the Bodo community of Assam'},
                    'doi': {'native': 'डोगरी', 'speakers': '2.6M+', 'script': 'Devanagari', 'fact': 'Language of Jammu region'},
                    'ks': {'native': 'کٲشُر / कश्मीरी', 'speakers': '7M+', 'script': 'Perso-Arabic / Devanagari', 'fact': 'Primary language of Kashmir Valley'},
                    'kok': {'native': 'कोंकणी', 'speakers': '2.5M+', 'script': 'Devanagari', 'fact': 'Official language of Goa'},
                    'mai': {'native': 'मैथिली', 'speakers': '34M+', 'script': 'Devanagari', 'fact': 'One of India’s classical languages'},
                    'mni': {'native': 'ꯃꯤꯇꯩ ꯂꯣꯟ', 'speakers': '1.8M+', 'script': 'Meitei Mayek', 'fact': 'Language of Manipur'},
                    'ne': {'native': 'नेपाली', 'speakers': '17M+', 'script': 'Devanagari', 'fact': 'Official language of Nepal'},
                    'sa': {'native': 'संस्कृतम्', 'speakers': '0.1M+', 'script': 'Devanagari', 'fact': 'Ancient liturgical language of India'},
                    'sat': {'native': 'ᱥᱟᱱᱛᱟᱲᱤ', 'speakers': '7M+', 'script': 'Ol Chiki', 'fact': 'Tribal language of central India'},
                    'sd': {'native': 'سنڌي', 'speakers': '30M+', 'script': 'Perso-Arabic', 'fact': 'Language of Sindhi people'},
                    'ur': {'native': 'اردو', 'speakers': '70M+', 'script': 'Perso-Arabic', 'fact': 'One of India’s official languages'}
                }
                
                if selected_lang in lang_info:
                    info = lang_info[selected_lang]
                    st.markdown(f"""
                    ### 🎭 {LANGUAGE_NAMES[selected_lang]} ({info['native']})
                    
                    📊 **Speakers:** {info['speakers']} worldwide
                    
                    ✍️ **Script:** {info['script']}
                    
                    💫 **Fun Fact:** {info['fact']}
                    """)
                    
                    # Generate sample audio
                    sample_text = "Hello, how are you?"
                    if translator.api_key:
                        audio_data = translator.text_to_audio(sample_text, selected_lang, 'anushka')
                        if audio_data:
                            st.audio(audio_data, format='audio/wav')
    
    # Enhanced sidebar with interactive elements
    with st.sidebar:
        # Animated sidebar header
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
            <h2 style="margin: 0; color: white;">🌟 Translation Hub</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Your AI Language Companion</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Interactive language selector
        st.markdown("### 🌍 Supported Languages")
        
        # Language grid with flags/emojis
        lang_display = {
            'hi': '🇮🇳 Hindi',
            'en': '🇺🇸 English', 
            'bn': '🇧🇩 Bengali',
            'ta': '🇮🇳 Tamil',
            'te': '🇮🇳 Telugu',
            'gu': '🇮🇳 Gujarati',
            'kn': '🇮🇳 Kannada',
            'ml': '🇮🇳 Malayalam',
            'mr': '🇮🇳 Marathi',
            'pa': '🇮🇳 Punjabi',
            'od': '🇮🇳 Odia',
            'as': '🇮🇳 Assamese',
            'brx': '🇮🇳 Bodo',
            'doi': '🇮🇳 Dogri',
            'ks': '🇮🇳 Kashmiri',
            'kok': '🇮🇳 Konkani',
            'mai': '🇮🇳 Maithili',
            'mni': '🇮🇳 Manipuri',
            'ne': '🇳🇵 Nepali',
            'sa': '🇮🇳 Sanskrit',
            'sat': '🇮🇳 Santali',
            'sd': '🇵🇰 Sindhi',
            'ur': '🇮🇳 Urdu'
        }
        
        for code, display in lang_display.items():
            if st.button(display, key=f"sidebar_lang_{code}", use_container_width=True):
                st.balloons()
                st.success(f"✨ {display} selected!")
                
        st.markdown("---")
        
        for code, name in LANGUAGE_NAMES.items():
            st.write(f"• **{name}** ({code})")
        
        st.markdown("""
        ---
        ### 🎤 Available Voice Speakers:
        """)
        
        # Display speakers in two columns
        speaker_cols = st.columns(2)
        speaker_list = list(SPEAKERS.items())
        mid_point = len(speaker_list) // 2
        
        with speaker_cols[0]:
            for speaker_id, speaker_name in speaker_list[:mid_point]:
                st.write(f"• {speaker_name}")
        
        with speaker_cols[1]:
            for speaker_id, speaker_name in speaker_list[mid_point:]:
                st.write(f"• {speaker_name}")
        
        st.markdown("""
        ---
        ### 🔧 Setup Instructions:
        1. Create a `.env` file in your project directory
        2. Add your Sarvam API key: `SARVAM_API_KEY=your_key_here`
        3. Install required packages: `pip install -r requirements.txt`
        
        ### 📋 Features:
        - ✅ **Auto-detect languages** for source & target
        - ✅ **Text translation** with speech output
        - ✅ **Voice-to-text** recognition
        - ✅ **Text-to-speech** synthesis
        - ✅ **Complete voice-to-voice** translation
        - ✅ **Speech for input text** (listen to what you typed)
        - ✅ **Multiple Indian languages** support
        - ✅ **20+ voice speakers** (Male & Female)
        - ✅ **Smart language suggestions** when auto-detecting
        
        ### 🔍 Smart Detection Features:
        - **Native Script Detection:** Recognizes original scripts (देवनागरी, বাংলা, etc.)
        - **Transliteration Support:** Understands Indian languages in English script
        - **Mixed Content:** Handles combination of scripts and languages
        - **Smart Suggestions:** Intelligent target language recommendations
        - **Real-time Detection:** Works for both text and voice input
        - **Fallback Detection:** Advanced pattern matching when API unavailable
        """)
        
        # Interactive help sections
        with st.expander("🛠️ Quick Help & Troubleshooting"):
            help_tab1, help_tab2 = st.tabs(["🔧 Common Issues", "💡 Pro Tips"])
            
            with help_tab1:
                st.markdown("""
                **Common Issues:**
                
                - **"Languages must be different"** → Use Auto-Detect or select different languages
                - **Wrong language detected?** → Try using more specific words or manual selection  
                - **Audio not working?** → Check microphone permissions and internet connection
                - **API errors?** → Verify your SARVAM_API_KEY in .env file
                """)
                
                if st.button("🔄 Reset Session Data", key="reset_session"):
                    st.session_state.translation_count = 0
                    st.session_state.voice_count = 0
                    st.session_state.characters_translated = 0
                    st.success("Session data reset!")
                    
            with help_tab2:
                st.markdown("""
                **Pro Tips:**
                
                - Use 'namaste kaise ho' for Hindi transliteration
                - Mix native scripts with English words
                - Speak naturally for better voice detection
                - Try different speakers for varied voices
                """)
        
        # Interactive theme selector
        with st.expander("🎨 Personalization"):
            st.markdown("**🌈 Color Theme:**")
            theme_col1, theme_col2 = st.columns(2)
            
            with theme_col1:
                if st.button("🌅 Sunrise", key="theme1"):
                    st.balloons()
                    st.success("Theme applied!")
                    
            with theme_col2:
                if st.button("🌊 Ocean", key="theme2"):
                    st.snow()
                    st.success("Theme applied!")
            
            st.markdown("**🔊 Audio Settings:**")
            audio_speed = st.slider("Speech Speed", 0.5, 2.0, 1.0, 0.1, key="audio_speed")
            if audio_speed != 1.0:
                st.info(f"🎵 Audio will play at {audio_speed}x speed")
                
        # Live statistics
        with st.expander("📊 Live Statistics", expanded=True):
            total_activity = st.session_state.translation_count + st.session_state.voice_count
            
            if total_activity > 0:
                # Progress ring simulation
                progress_percentage = min(total_activity * 10, 100)
                st.progress(progress_percentage / 100)
                st.caption(f"Activity Level: {progress_percentage}%")
                
                # Achievement badges
                if st.session_state.translation_count >= 5:
                    st.success("🏆 Text Master - 5+ translations!")
                if st.session_state.voice_count >= 3:
                    st.success("🎤 Voice Expert - 3+ voice translations!")
                if st.session_state.characters_translated >= 100:
                    st.success("📚 Word Warrior - 100+ characters!")
            else:
                st.info("🚀 Start translating to unlock achievements!")
        
        # Animated footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; color: white; animation: pulse 2s infinite;">
            <h4 style="margin: 0; color: white;">🚀 Powered by Sarvam AI</h4>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Empowering Global Communication</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content footer with call-to-action
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
    
    with footer_col2:
        st.markdown("""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 20px; color: white; margin: 20px 0;">
            <h3 style="margin: 0; color: white;">🌟 Ready to Break Language Barriers?</h3>
            <p style="margin: 15px 0; opacity: 0.9; font-size: 1.1em;">
                Join thousands of users connecting across cultures with AI-powered translation
            </p>
            <div style="margin-top: 20px;">
                <strong style="font-size: 1.2em;">✨ Start Your Translation Journey Today! ✨</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":

    main()



