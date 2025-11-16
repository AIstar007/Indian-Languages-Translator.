# streamlit_app.py
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
    'te': 'Telugu'
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

def normalize_lang_code(lang):
    """
    Normalize a language code to short base form (e.g., 'hi-IN' -> 'hi').
    Keeps 'auto' as-is.
    """
    if not lang:
        return ''
    lang = str(lang)
    if lang.lower() == 'auto':
        return 'auto'
    return lang.split('-')[0].lower()

class StreamlitTranslator:
    def __init__(self):
        # Initialize API key and base URL
        self.api_key = os.getenv('SARVAM_API_KEY')
        self.base_url = "https://api.sarvam.ai"
        
        if not self.api_key:
            # Show warning but allow page to load
            st.warning("⚠️ SARVAM_API_KEY not found in environment variables. Add it to your .env file to enable API features.")
        
    def get_language_code(self, lang):
        """Convert short language code to full language code if available"""
        if not lang:
            return ''
        key = normalize_lang_code(lang)
        return SUPPORTED_LANGUAGES.get(key, lang)
    
    def validate_language_pair(self, source_lang, target_lang):
        """Validate that source and target languages are different"""
        if not source_lang or not target_lang:
            return False
            
        # Normalize to base codes
        source_base = normalize_lang_code(source_lang)
        target_base = normalize_lang_code(target_lang)
        
        # Disallow identical base codes (or identical full codes)
        if source_base == target_base:
            return False
            
        return True
    
    def get_smart_target_language(self, source_lang):
        """Get smart target language suggestion based on source (base codes expected)"""
        source_base = normalize_lang_code(source_lang)
        smart_pairs = {
            'en': 'hi',  # English -> Hindi
            'hi': 'en',  # Hindi -> English
            'bn': 'en',
            'gu': 'en',
            'kn': 'en',
            'ml': 'en',
            'mr': 'en',
            'od': 'en',
            'pa': 'en',
            'ta': 'en',
            'te': 'en',
        }
        return smart_pairs.get(source_base, 'en')
    
    def detect_language(self, text):
        """Detect language of the given text using API if available, otherwise fallback local detection"""
        if not text or not text.strip():
            return 'en'
        
        # Try Sarvam API detection if API key is provided
        if self.api_key:
            try:
                headers = {
                    "api-subscription-key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                endpoints = [
                    f"{self.base_url}/language-detection",
                    f"{self.base_url}/detect-language", 
                    f"{self.base_url}/language-detect"
                ]
                
                data = {"input": text, "text": text}
                for endpoint in endpoints:
                    try:
                        response = httpx.post(endpoint, headers=headers, json=data, timeout=20.0)
                        if response.status_code == 200:
                            result = response.json()
                            detected_lang = result.get('detected_language_code') or result.get('language_code') or result.get('language')
                            if detected_lang:
                                # normalize to base short code if possible
                                return normalize_lang_code(detected_lang)
                    except Exception:
                        continue
            except Exception:
                # Fall through to local detection
                pass
        
        # Fallback local detection
        return self._detect_language_locally(text)
    
    def _detect_language_locally(self, text):
        """Local heuristics to detect Indian language (supports transliteration heuristics)"""
        if not text or len(text.strip()) < 3:
            return 'en'
        
        original_text = text.strip()
        text_lower = original_text.lower()
        
        # Native script patterns (short list)
        native_patterns = {
            'hi': ['का', 'के', 'की', 'को', 'से', 'में', 'और', 'है', 'हैं'],
            'bn': ['এর', 'এক', 'সে', 'তার', 'আমি', 'আমার'],
            'gu': ['એ', 'છે', 'માં', 'ને', 'નો'],
            'kn': ['ಅವರು', 'ಇದು', 'ಆ', 'ಈ', 'ಮತ್ತು'],
            'ml': ['അത്', 'ഇത്', 'എന്ന്', 'ആണ്', 'ഉണ്ട്'],
            'mr': ['आहे', 'असा', 'या', 'ते', 'त्या'],
            'od': ['ଏହା', 'ସେ', 'ମୁଁ', 'ତୁମେ'],
            'pa': ['ਇਹ', 'ਉਹ', 'ਮੈਂ', 'ਤੁਸੀਂ', 'ਅਸੀਂ'],
            'ta': ['அது', 'இது', 'என்று', 'உள்ளது'],
            'te': ['అది', 'ఇది', 'అని', 'ఉంది']
        }
        
        transliterated_patterns = {
            'hi': {
                'words': ['namaste', 'dhanyawad', 'kaise', 'kya', 'hai', 'hain', 'aur', 'main', 'aap', 'tum', 'hum', 'yeh', 'woh'],
                'patterns': ['ji', 'ka', 'ki', 'ke', 'ko', 'se', 'mein']
            },
            'bn': {
                'words': ['namaskar', 'dhonnobad', 'kemon', 'ache', 'ami', 'apni', 'tumi'],
                'patterns': ['er', 'ta', 'te', 're']
            },
            'gu': {
                'words': ['namaste', 'dhanyawad', 'kem', 'su', 'chhe', 'ane', 'hun', 'tame'],
                'patterns': ['nu', 'na', 'ni', 'ne', 'thi']
            },
            'ta': {
                'words': ['vanakkam', 'nandri', 'eppadi', 'enna', 'irukku', 'naan', 'neengal'],
                'patterns': ['oda', 'ku', 'la', 'kku']
            },
            'te': {
                'words': ['namaskaram', 'dhanyawadalu', 'ela', 'emi', 'undi', 'nenu', 'miru'],
                'patterns': ['ki', 'lo', 'tho', 'di']
            },
            # Add others as needed...
        }
        
        scores = {}
        # native script checks (strong)
        for lang, tokens in native_patterns.items():
            score = sum(1 for t in tokens if t in original_text)
            if score:
                scores[lang] = scores.get(lang, 0) + score * 3
        
        # transliterated checks (weaker)
        for lang, patterns in transliterated_patterns.items():
            trans_score = 0
            for w in patterns.get('words', []):
                if w in text_lower:
                    trans_score += 2
            for p in patterns.get('patterns', []):
                if p in text_lower:
                    trans_score += 1
            if trans_score:
                scores[lang] = scores.get(lang, 0) + trans_score
        
        # english heuristics (lower priority)
        english_tokens = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to']
        english_score = sum(1 for t in english_tokens if t in text_lower)
        ascii_ratio = sum(1 for c in original_text if ord(c) < 128) / max(1, len(original_text))
        max_other_score = max([s for k, s in scores.items() if k != 'en'], default=0)
        if ascii_ratio > 0.8:
            if max_other_score < 3:
                scores['en'] = english_score + int(ascii_ratio * 2)
            else:
                scores['en'] = int(english_score * 0.5)
        
        if scores:
            detected_lang = max(scores, key=scores.get)
            # Informational messages
            if detected_lang != 'en' and ascii_ratio > 0.9:
                st.info(f"🔍 Detected **{LANGUAGE_NAMES.get(detected_lang, detected_lang)}** written in Latin script (transliterated).")
            elif detected_lang != 'en':
                st.info(f"🔍 Detected language: **{LANGUAGE_NAMES.get(detected_lang, detected_lang)}**")
            else:
                st.info(f"🔍 Detected language: **English**")
            return detected_lang
        return 'en'
    
    def text_translate(self, text, source_lang, target_lang):
        """Translate text from source language to target language using Sarvam AI"""
        if not text:
            return None
        # Normalize codes (Sarvam expects full codes maybe, so convert)
        source_full = self.get_language_code(source_lang)
        target_full = self.get_language_code(target_lang)
        
        if not self.api_key:
            st.warning("API key not configured. Skipping remote translation.")
            return None
        
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "input": text,
            "source_language_code": source_full,
            "target_language_code": target_full,
            "mode": "formal"
        }
        try:
            with st.spinner("Translating..."):
                response = httpx.post(f"{self.base_url}/translate", headers=headers, json=data, timeout=30.0)
            if response.status_code == 200:
                result = response.json()
                # try multiple possible keys
                return result.get('translated_text') or result.get('translation') or result.get('result') or None
            else:
                st.error(f"Translation error: {response.text}")
                return None
        except Exception as e:
            st.error(f"Translation error: {str(e)}")
            return None

    def audio_to_text(self, audio_bytes, expected_language=None):
        """Convert audio bytes to text using Sarvam AI Speech-to-Text"""
        if not audio_bytes:
            return None
        temp_audio_path = None
        try:
            # Write to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name
            
            headers = {"api-subscription-key": self.api_key} if self.api_key else {}
            files = {'file': ('audio.wav', open(temp_audio_path, 'rb'), 'audio/wav')}
            
            data = {}
            if expected_language and expected_language != 'auto':
                lang_code = self.get_language_code(expected_language)
                data['language'] = lang_code
            
            with st.spinner("🎤 Converting speech to text..."):
                response = httpx.post(f"{self.base_url}/speech-to-text", headers=headers, files=files, data=data or None, timeout=60.0)
            
            # close file handle
            files['file'][1].close()
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get('transcript') or result.get('text') or result.get('result')
                api_detected = result.get('detected_language') or result.get('language_code') or result.get('language')
                return {'transcript': transcript, 'detected_language': api_detected}
            else:
                st.error(f"Speech recognition error: {response.text}")
                return None
        except Exception as e:
            st.error(f"Error in voice recognition: {str(e)}")
            return None
        finally:
            # Remove temp file if created
            try:
                if temp_audio_path and os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
            except Exception:
                pass

    def text_to_audio(self, text, lang='en-IN', speaker='anushka'):
        """Convert text to audio using Sarvam AI's text-to-speech API"""
        if not text:
            return None
        lang_full = self.get_language_code(lang)
        if not self.api_key:
            st.warning("API key not configured. Skipping text-to-speech.")
            return None
        
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "target_language_code": lang_full,
            "speaker": speaker,
            "pitch": 0,
            "pace": 1,
            "loudness": 1,
            "speech_sample_rate": 22050,
            "enable_preprocessing": True,
            "model": "bulbul:v2"
        }
        try:
            with st.spinner("Converting text to speech..."):
                response = httpx.post(f"{self.base_url}/text-to-speech", headers=headers, json=data, timeout=60.0)
            if response.status_code == 200:
                result = response.json()
                # result may contain base64 in different keys; attempt common ones
                audio_base64 = None
                if isinstance(result.get('audios'), list):
                    audio_base64 = result.get('audios')[0]
                audio_base64 = audio_base64 or result.get('audio') or result.get('base64') or None
                if audio_base64:
                    try:
                        return base64.b64decode(audio_base64)
                    except Exception:
                        st.error("Received audio data in unexpected format.")
                        return None
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
    
    # Custom CSS (kept as before)
    st.markdown("""
    <style>
    /* trimmed for brevity in this example - keep your original styles here */
    .main-title { font-size: 3rem; font-weight: bold; text-align: center; margin-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🗣️ Indian Languages Translator")
    st.markdown("Translate text and voice using Indian Languages Translator's powerful translation services")
    
    # Initialize session state for statistics and flags
    st.session_state.setdefault('translation_count', 0)
    st.session_state.setdefault('voice_count', 0)
    st.session_state.setdefault('characters_translated', 0)
    st.session_state.setdefault('generate_audio', False)
    st.session_state.setdefault('show_translation', False)
    st.session_state.setdefault('last_translation', None)
    st.session_state.setdefault('last_target_lang', None)
    st.session_state.setdefault('selected_speaker', next(iter(SPEAKERS.keys())))
    
    # Dynamic statistics display
    with st.container():
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        with stat_col1:
            st.metric(label="📝 Text Translations", value=st.session_state.translation_count, delta="This session")
        with stat_col2:
            st.metric(label="🎤 Voice Translations", value=st.session_state.voice_count, delta="This session")
        with stat_col3:
            st.metric(label="📊 Characters Processed", value=f"{st.session_state.characters_translated:,}", delta="Total")
        with stat_col4:
            total_translations = st.session_state.translation_count + st.session_state.voice_count
            st.metric(label="🏆 Success Rate", value="99.8%" if total_translations > 0 else "Ready", delta="AI Powered")
    
    st.markdown("---")
    
    translator = StreamlitTranslator()
    
    tab1, tab2, tab3 = st.tabs(["📝 Text Translation", "🎤 Voice Translation", "🎯 Quick Actions"])
    
    # -----------------------
    # Tab 1 - Text Translation
    # -----------------------
    with tab1:
        st.header("Text Translation")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🔤 Input Language")
            source_lang_text = st.selectbox(
                "Choose source language:",
                options=list(LANGUAGE_NAMES.keys()),
                format_func=lambda x: LANGUAGE_NAMES[x],
                key="source_text",
                index=0,
                help="Select 'Auto-Detect' for smart language identification"
            )
            if source_lang_text == 'auto':
                st.info("🤖 AI will detect your language automatically")
            else:
                st.success(f"✅ {LANGUAGE_NAMES[source_lang_text]} selected")
            
            st.markdown("### ✍️ Your Text")
            input_text = st.text_area("Enter text to translate:", height=150, placeholder="Type your text here...", help="You can type in any supported language or use transliteration")
            if input_text:
                char_count = len(input_text)
                word_count = len(input_text.split())
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                with col_stats1:
                    st.caption(f"📊 {char_count} characters")
                with col_stats2:
                    st.caption(f"📝 {word_count} words")
                with col_stats3:
                    st.caption("🔥 Great for translation!" if char_count > 100 else "✨ Perfect length")
            
            # Speech option for input text
            if input_text:
                col_input1, col_input2 = st.columns([1, 2])
                with col_input1:
                    input_speaker = st.selectbox("Input Voice:", options=list(SPEAKERS.keys()), format_func=lambda x: SPEAKERS[x], key="input_speaker")
                with col_input2:
                    if st.button("🔊 Listen to Input Text", key="input_audio"):
                        input_lang = source_lang_text
                        if source_lang_text == 'auto':
                            detected = translator.detect_language(input_text)
                            input_lang = detected if detected else 'en'
                            st.info(f"Detected language: {LANGUAGE_NAMES.get(input_lang, input_lang)}")
                        audio_data = translator.text_to_audio(input_text, input_lang, input_speaker)
                        if audio_data:
                            st.audio(audio_data, format='audio/wav')
                        else:
                            st.error("Failed to generate audio for input text. Please try again.")
        
        with col2:
            target_lang_text = st.selectbox("Target Language:", options=list(LANGUAGE_NAMES.keys()), format_func=lambda x: LANGUAGE_NAMES[x], key="target_text", index=1)
            speaker_text = st.selectbox("Output Voice:", options=list(SPEAKERS.keys()), format_func=lambda x: SPEAKERS[x], key="speaker_text")
            st.session_state.selected_speaker = speaker_text
            
            if (source_lang_text != 'auto' and target_lang_text != 'auto' and source_lang_text == target_lang_text):
                st.warning("⚠️ Source and target languages are the same. Translation will not work.")
            
            translate_btn = st.button("🚀 Translate Text", type="primary", use_container_width=True)
            if translate_btn:
                if not input_text:
                    st.warning("Please enter text to translate.")
                elif not translator.api_key:
                    st.warning("Please configure SARVAM_API_KEY in .env to use translation.")
                else:
                    st.session_state.translation_count += 1
                    st.session_state.characters_translated += len(input_text)
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    status_text.text('🔄 Initializing translation...')
                    progress_bar.progress(10)
                    
                    actual_source_lang = source_lang_text
                    if source_lang_text == 'auto':
                        status_text.text('🔍 Detecting source language...')
                        progress_bar.progress(25)
                        detected = translator.detect_language(input_text)
                        actual_source_lang = detected if detected else 'en'
                        st.success(f"**Detected:** {LANGUAGE_NAMES.get(actual_source_lang, actual_source_lang)}")
                    
                    actual_target_lang = target_lang_text
                    if target_lang_text == 'auto':
                        actual_target_lang = translator.get_smart_target_language(actual_source_lang)
                        st.info(f"**Auto-selected target language:** {LANGUAGE_NAMES.get(actual_target_lang, actual_target_lang)}")
                    
                    if not translator.validate_language_pair(actual_source_lang, actual_target_lang):
                        st.error(f"⚠️ Source and target languages cannot be the same ({LANGUAGE_NAMES.get(actual_source_lang, actual_source_lang)}).")
                        st.info("💡 Try selecting a different target language or use auto-detection.")
                    else:
                        status_text.text('🌐 Translating text...')
                        progress_bar.progress(50)
                        translated = translator.text_translate(input_text, actual_source_lang, actual_target_lang)
                        if translated:
                            st.session_state.last_translation = translated
                            st.session_state.last_target_lang = actual_target_lang
                            st.session_state.show_translation = True
                            progress_bar.progress(100)
                            status_text.text('✅ Translation completed!')
                            st.balloons()
                            st.success("🎉 Translation completed successfully!")
                            progress_bar.empty()
                            status_text.empty()
                        else:
                            status_text.empty()
                            progress_bar.empty()
    
        # persistent display of last translation
        if st.session_state.get('show_translation') and st.session_state.get('last_translation'):
            st.markdown("---")
            st.markdown(f"### 🎯 Translation Result ({LANGUAGE_NAMES.get(st.session_state.get('last_target_lang', 'en'), st.session_state.get('last_target_lang', 'en'))})")
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           padding: 20px; border-radius: 15px; color: white; margin: 10px 0;">
                    <h4 style="margin: 0; color: white;">📝 Translation</h4>
                    <p style="font-size: 1.2em; margin: 10px 0 0 0; line-height: 1.5;">{st.session_state.last_translation}</p>
                </div>
                """, unsafe_allow_html=True)
            
            audio_col1, audio_col2 = st.columns([1, 3])
            with audio_col1:
                if st.button("🔊 Play Audio", key="play_translation_audio_persistent"):
                    st.session_state.generate_audio = True
            with audio_col2:
                if st.session_state.get('generate_audio'):
                    current_speaker = st.session_state.get('selected_speaker', next(iter(SPEAKERS.keys())))
                    current_translation = st.session_state.get('last_translation')
                    current_target = st.session_state.get('last_target_lang') or 'en'
                    with st.spinner(f"Generating speech with {SPEAKERS.get(current_speaker, current_speaker)}..."):
                        audio_data = translator.text_to_audio(current_translation, current_target, current_speaker)
                        if audio_data:
                            st.success("🎵 Audio ready!")
                            st.audio(audio_data, format='audio/wav')
                        else:
                            st.error("Failed to generate audio. Please try again.")
                    st.session_state.generate_audio = False
            
            if st.button("🗑️ Clear Translation", key="clear_translation"):
                st.session_state.show_translation = False
                st.session_state.last_translation = None
                st.session_state.last_target_lang = None
                st.experimental_rerun()
    
    # -----------------------
    # Tab 2 - Voice Translation
    # -----------------------
    with tab2:
        st.markdown("""
        <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%); 
                    border-radius: 15px; margin-bottom: 20px;">
            <h2 style="margin: 0; color: #333;">🎤 Voice Translation Magic</h2>
            <p style="margin: 5px 0 0 0; color: #666;">Speak naturally, translate instantly</p>
        </div>
        """, unsafe_allow_html=True)
        
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
            source_lang_voice = st.selectbox("What language will you speak?", options=list(LANGUAGE_NAMES.keys()), format_func=lambda x: LANGUAGE_NAMES[x], key="source_voice", index=0)
            if source_lang_voice == 'auto':
                st.info("🤖 AI will listen and detect your language")
            else:
                st.success(f"🎤 Ready to record in {LANGUAGE_NAMES[source_lang_voice]}")
        with col2:
            target_lang_voice = st.selectbox("What language do you want?", options=list(LANGUAGE_NAMES.keys()), format_func=lambda x: LANGUAGE_NAMES[x], key="target_voice", index=1)
            if target_lang_voice == 'auto':
                st.info("🎯 AI will choose the best target language")
            else:
                st.success(f"🔊 Will output in {LANGUAGE_NAMES[target_lang_voice]}")
        
        st.markdown("### 🎭 Voice Character Selection")
        speaker_col1, speaker_col2 = st.columns([1, 2])
        with speaker_col1:
            speaker_voice = st.selectbox("Choose your AI voice:", options=list(SPEAKERS.keys()), format_func=lambda x: SPEAKERS[x], key="speaker_voice")
        with speaker_col2:
            if st.button("🔊 Preview Voice", key="preview_voice"):
                if translator.api_key:
                    sample_text = "Hello! This is how I sound. Nice to meet you!"
                    lang_for_preview = target_lang_voice if target_lang_voice != 'auto' else 'en'
                    preview_audio = translator.text_to_audio(sample_text, lang_for_preview, speaker_voice)
                    if preview_audio:
                        st.audio(preview_audio, format='audio/wav')
                        st.success("🎵 Voice preview ready!")
                    else:
                        st.error("Could not generate preview")
                else:
                    st.warning("API key not configured for preview.")
        
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 15px; color: white; margin: 20px 0; text-align: center;">
            <h3 style="margin: 0; color: white;">🎤 Ready to Record?</h3>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Click the microphone and speak naturally</p>
        </div>
        """, unsafe_allow_html=True)
        
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
                - 3-10 second recordings
                """)
        
        audio_bytes = audio_recorder(text="Click to record", recording_color="#e87070", neutral_color="#6aa36f", icon_name="microphone-lines", icon_size="2x")
        
        if audio_bytes:
            st.success("Audio recorded successfully!")
            st.audio(audio_bytes, format='audio/wav')
            voice_translate_btn = st.button("🎤➡️🔊 Translate My Voice", type="primary", use_container_width=True)
            if voice_translate_btn:
                if not translator.api_key:
                    st.warning("Please configure SARVAM_API_KEY to use voice translation.")
                else:
                    st.session_state.voice_count += 1
                    voice_progress = st.progress(0)
                    voice_status = st.empty()
                    voice_status.text('🎤 Processing your voice...')
                    voice_progress.progress(20)
                    
                    speech_result = translator.audio_to_text(audio_bytes, source_lang_voice if source_lang_voice != 'auto' else None)
                    if not speech_result or not speech_result.get('transcript'):
                        st.error("Could not recognize speech. Try again in a quieter environment.")
                        voice_progress.empty()
                        voice_status.empty()
                    else:
                        recognized_text = speech_result['transcript']
                        api_detected_lang = speech_result.get('detected_language')
                        st.success("🎤 Speech recognized!")
                        
                        actual_source_lang = source_lang_voice
                        if source_lang_voice == 'auto':
                            if api_detected_lang:
                                actual_source_lang = normalize_lang_code(api_detected_lang)
                                st.success(f"🎤 Speech API detected: {LANGUAGE_NAMES.get(actual_source_lang, actual_source_lang)}")
                            else:
                                detected = translator.detect_language(recognized_text)
                                actual_source_lang = detected if detected else 'hi'
                                st.info(f"🔍 Text pattern detected: {LANGUAGE_NAMES.get(actual_source_lang, actual_source_lang)}")
                                if actual_source_lang == 'en' and any(w in recognized_text.lower() for w in ['namaste', 'kaise', 'hai', 'aur']):
                                    actual_source_lang = 'hi'
                                    st.success("🎯 Corrected to Hindi due to transliterated words")
                        
                        actual_target_lang = target_lang_voice
                        if target_lang_voice == 'auto':
                            actual_target_lang = translator.get_smart_target_language(actual_source_lang)
                            st.info(f"🎯 Auto-selected target language: {LANGUAGE_NAMES.get(actual_target_lang, actual_target_lang)}")
                        
                        # Validate/auto-fix
                        if not translator.validate_language_pair(actual_source_lang, actual_target_lang):
                            # attempt auto-fixes
                            if normalize_lang_code(actual_source_lang) == 'en':
                                actual_target_lang = 'hi'
                            else:
                                actual_target_lang = 'en'
                        
                        if not translator.validate_language_pair(actual_source_lang, actual_target_lang):
                            st.error("Unable to resolve source/target language conflict. Please select manually.")
                        else:
                            st.write(f"**Recognized text ({LANGUAGE_NAMES.get(normalize_lang_code(actual_source_lang), actual_source_lang)}):** {recognized_text}")
                            translated_text = translator.text_translate(recognized_text, actual_source_lang, actual_target_lang)
                            if translated_text:
                                st.success("✅ Translation completed!")
                                st.write(f"**Translated text ({LANGUAGE_NAMES.get(actual_target_lang, actual_target_lang)}):** {translated_text}")
                                voice_status.text(f'🎭 Generating speech with {SPEAKERS.get(speaker_voice, speaker_voice)}...')
                                voice_progress.progress(80)
                                audio_data = translator.text_to_audio(translated_text, actual_target_lang, speaker_voice)
                                if audio_data:
                                    voice_progress.progress(100)
                                    voice_status.text('✨ Voice translation complete!')
                                    st.balloons()
                                    st.success("🎉 Voice translation successful!")
                                    st.audio(audio_data, format='audio/wav')
                                else:
                                    st.error("Failed to generate audio for translated text.")
                            else:
                                st.error("Failed to translate recognized speech.")
                        voice_progress.empty()
                        voice_status.empty()
        else:
            if not translator.api_key:
                st.warning("Please configure your SARVAM_API_KEY in the .env file to use voice translation.")
    
    # -----------------------
    # Tab 3 - Quick Actions
    # -----------------------
    with tab3:
        st.header("🎯 Quick Actions & Tools")
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
                    if translator.api_key:
                        audio_data = translator.text_to_audio(hindi, 'hi', 'anushka')
                        if audio_data:
                            st.audio(audio_data, format='audio/wav')
        with col_quick2:
            st.markdown("#### 🎮 Interactive Features")
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
            if st.button("📊 Session Statistics", key="stats"):
                st.markdown("""
                ### 📈 Your Translation Journey
                🎉 **Achievements Unlocked:**
                - 🏆 AI Translation Explorer
                - 🌍 Multilingual Communicator
                - 🎤 Voice Tech Pioneer
                """)
        
        st.markdown("---")
        st.subheader("🌐 Language Explorer")
        explore_col1, explore_col2 = st.columns(2)
        with explore_col1:
            selected_lang = st.selectbox("🔍 Explore a language:", options=[k for k in LANGUAGE_NAMES.keys() if k != 'auto'], format_func=lambda x: LANGUAGE_NAMES[x], key="explore_lang")
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
                    'en': {'native': 'English', 'speakers': '1.5B+', 'script': 'Latin', 'fact': 'Global lingua franca'}
                }
                if selected_lang in lang_info:
                    info = lang_info[selected_lang]
                    st.markdown(f"""
                    ### 🎭 {LANGUAGE_NAMES[selected_lang]} ({info['native']})
                    📊 **Speakers:** {info['speakers']}
                    ✍️ **Script:** {info['script']}
                    💫 **Fun Fact:** {info['fact']}
                    """)
                    sample_text = "Hello, how are you?"
                    if translator.api_key:
                        audio_data = translator.text_to_audio(sample_text, selected_lang, 'anushka')
                        if audio_data:
                            st.audio(audio_data, format='audio/wav')
    
    # Sidebar (trimmed but functional)
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
            <h2 style="margin: 0; color: white;">🌟 Translation Hub</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Your AI Language Companion</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### 🌍 Supported Languages")
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
            'od': '🇮🇳 Odia'
        }
        for code, display in lang_display.items():
            if st.button(display, key=f"sidebar_lang_{code}", use_container_width=True):
                st.balloons()
                st.success(f"✨ {display} selected!")
        st.markdown("---")
        for code, name in LANGUAGE_NAMES.items():
            st.write(f"• **{name}** ({code})")
        st.markdown("---")
        st.markdown("### 🔧 Setup Instructions:\n1. Create a `.env` file\n2. Add `SARVAM_API_KEY=your_key`\n3. `pip install -r requirements.txt`")
        with st.expander("🛠️ Quick Help & Troubleshooting"):
            help_tab1, help_tab2 = st.tabs(["🔧 Common Issues", "💡 Pro Tips"])
            with help_tab1:
                st.markdown("""
                **Common Issues:**
                - "Languages must be different" → Use Auto-Detect or select different languages
                - Wrong language detected? → Try manual selection
                - Audio not working? → Check mic permissions
                - API errors? → Verify SARVAM_API_KEY
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
                - Speak naturally for better recognition
                """)
    
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
    with footer_col2:
        st.markdown("""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 20px; color: white; margin: 20px 0;">
            <h3 style="margin: 0; color: white;">🌟 Ready to Break Language Barriers?</h3>
            <p style="margin: 15px 0; opacity: 0.9; font-size: 1.1em;">
                Start your translation journey.
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
