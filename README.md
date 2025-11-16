# 🗣️ Sarvam AI Translator

A powerful, multilingual translation application powered by Sarvam AI that supports both text and voice translation with advanced auto-detection capabilities.

![Sarvam AI Translator](https://img.shields.io/badge/Powered%20by-Sarvam%20AI-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)

## ✨ Features

### 🎯 **Smart Language Detection**
- **Auto-detect source languages** - Automatically identifies the language of your input
- **Transliteration support** - Understands Indian languages written in English script
- **Pattern recognition** - Advanced algorithms to detect mixed-script content
- **Smart pairing** - Intelligent target language suggestions

### 📝 **Text Translation**
- **Multi-script support** - Native scripts (देवनागरी, বাংলা, ગુજરાતી, etc.)
- **Transliterated input** - Write Hindi as "namaste kaise ho" 
- **Mixed content** - Combine English and regional language words
- **Input speech** - Listen to your typed text before translation
- **Output speech** - Automatic text-to-speech for translations

### 🎤 **Voice Translation**
- **Voice-to-voice translation** - Complete speech-to-speech workflow
- **Real-time recording** - Built-in microphone support in web browser  
- **Speech recognition** - Advanced speech-to-text using Sarvam AI
- **Voice synthesis** - Natural-sounding speech output
- **Auto-detection** - Identifies language from your speech

### 🔊 **Advanced Speech Features**
- **20+ Voice Options** - Male and female speakers for all languages
- **Custom speaker selection** - Choose different voices for input and output
- **High-quality synthesis** - Natural-sounding speech using Sarvam AI's TTS
- **Audio playback controls** - Built-in audio player with controls

### 🌐 **Supported Languages**
- **Hindi** (हिंदी) - hi
- **English** - en  
- **Bengali** (বাংলা) - bn
- **Tamil** (தமிழ்) - ta
- **Telugu** (తెలుగు) - te
- **Gujarati** (ગુજરાતી) - gu
- **Kannada** (ಕನ್ನಡ) - kn
- **Malayalam** (മലയാളം) - ml
- **Marathi** (मराठी) - mr
- **Odia** (ଓଡ଼ିଆ) - od
- **Punjabi** (ਪੰਜਾਬੀ) - pa

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Sarvam AI API key
- Microphone access (for voice features)

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd sarvam-translator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project directory:
   ```env
   SARVAM_API_KEY=your_sarvam_api_key_here
   ```

4. **Run the application**
   
   **Option 1:** Double-click `run_webapp.bat` (Windows)
   
   **Option 2:** Command line
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open in browser**
   
   Navigate to `http://localhost:8501`

## 🎯 Usage Guide

### Text Translation

1. **Select languages** or use "🔍 Auto-Detect"
2. **Type your text** in the input box
   - Native script: `नमस्ते कैसे हो`  
   - Transliterated: `namaste kaise ho`
   - Mixed: `main office जाऊंगा`
3. **Choose voice speaker** for output
4. **Click "Translate Text"**
5. **Listen to translation** - Audio plays automatically

### Voice Translation

1. **Set source/target languages** or use "🔍 Auto-Detect"  
2. **Choose voice speaker** for output
3. **Click the microphone** to record
4. **Speak clearly** in your chosen language
5. **Click "Translate Voice"**
6. **Get complete voice-to-voice translation**

### Transliteration Examples

The app understands Indian languages written in English script:

| Language | Transliterated Input | Native Script |
|----------|---------------------|---------------|
| Hindi | `namaste aap kaise hain` | नमस्ते आप कैसे हैं |
| Bengali | `namaskar kemon acho` | নমস্কার কেমন আছো |
| Tamil | `vanakkam eppadi irukkeergal` | வணக்கம் எப்படி இருக்கீர்கள் |
| Gujarati | `namaste kem chho` | નમસ્તે કેમ છો |

## 🎵 Voice Speakers

Choose from 20+ natural-sounding voice options:

### Female Voices
- Anushka, Manisha, Vidya, Isha, Ritu, Sakshi
- Priya, Neha, Pooja, Simran, Kavya

### Male Voices  
- Abhilash, Arya, Karun, Hitesh, Aditya, Chirag
- Harsh, Rahul, Rohan

## 🛠️ Technical Details

### Architecture
- **Frontend:** Streamlit web application
- **Backend:** Sarvam AI API integration
- **Audio Processing:** Web-based audio recording and playback
- **Language Detection:** Multi-layer pattern matching + API detection

### API Integration
- **Translation:** Sarvam AI Translate API
- **Speech-to-Text:** Sarvam AI Speech Recognition  
- **Text-to-Speech:** Sarvam AI Voice Synthesis
- **Language Detection:** Pattern matching with API fallback

### File Structure
```
sarvam-translator/
├── streamlit_app.py      # Main Streamlit web application
├── translator.py         # Command-line translator
├── translator_backup.py  # Backup of original translator  
├── requirements.txt      # Python dependencies
├── run_webapp.bat       # Windows startup script
├── .env                 # Environment variables (API key)
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables
```env
SARVAM_API_KEY=your_api_key_here
```

### Customization Options
- **Default languages:** Modify `LANGUAGE_NAMES` in `streamlit_app.py`
- **Voice speakers:** Update `SPEAKERS` dictionary  
- **UI theme:** Streamlit configuration in `.streamlit/config.toml`

## 🐛 Troubleshooting

### Common Issues

**"Languages must be different" error**
- Ensure source and target languages are different
- Use "Auto-Detect" for smart language pairing

**Language detection not working**
- Use common words in your language for better detection
- Try transliterated input: `namaste` instead of just `hello`
- Mix native and English scripts

**Audio issues**
- Grant microphone permissions to your browser
- Check system audio settings
- Use a good quality microphone
- Speak clearly and slowly

**API errors**
- Verify your `SARVAM_API_KEY` in the `.env` file
- Check your Sarvam AI account credits
- Ensure stable internet connection

### Debug Features
- Use the "🔧 Debug Info" section in the voice translation tab
- Test language pairing before recording
- Check current language selections

## 📋 Development

### Running in Development Mode
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
streamlit run streamlit_app.py --server.runOnSave true
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- **Sarvam AI** - For providing powerful multilingual AI services
- **Streamlit** - For the amazing web app framework
- **Contributors** - Thanks to all who helped improve this project

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review Sarvam AI documentation

---

**Made with ❤️ using Sarvam AI and Streamlit**

*Empowering multilingual communication through AI*