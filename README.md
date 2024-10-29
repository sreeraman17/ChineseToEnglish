# 🌏 Chinese to English PDF Translator 🚀

> Transform your Chinese PDFs into English with just a few clicks! ✨

## 🎯 What's This All About?

A comprehensive web application that provides high-quality Chinese to English translation using the Qwen 2.5 model. With a sleek web interface that's as easy as drag-and-drop.

## Screenshot

![Screenshot of the Chinese to English PDF Translator](https://github.com/sreeraman17/ChineseToEnglish/blob/main/screenshot.jpg)

### ✨ Key Features

- 🎭 **Drag & Drop**: Toss your PDFs into our translator like a boss
- 📊 **Live Progress Tracking**: Watch your translation come to life in real-time
- 💫 **Smart Text Panels**: Edit both Chinese and English text on the fly
- 📋 **Copy with Style**: One-click copying for both languages
- 💾 **Download & Go**: Save your translations instantly
- 🔔 **Smart Notifications**: We'll keep you in the loop every step of the way with progress bar

## 🏗️ Under the Hood

### 🎨 Frontend UI
- Beautiful, responsive design that works everywhere
- Smooth animations and intuitive controls
- Rich text editing capabilities

### ⚙️ Backend Power
- **Flask**: Running the show behind the scenes
- **Smart Endpoints**:
  - `/upload`: Where the magic begins
  - `/status`: Keeping you informed

### 🔄 Translation Pipeline
1. 📑 PDF text extraction with pdfplumber
2. 🔍 Language verification with langdetect
3. 🎯 Translation magic with ollama
4. ✨ Instant results display

## 🚀 Getting Started

### 📋 Prerequisites
- Python 3.8+ (The newer, the better!)
- pip (Your friendly package installer)

### 🎮 Quick Start

1. **Clone the Magic**:
```bash
git clone https://github.com/sreeraman17/ChineseToEnglish
cd ChineseToEnglish
```

2. **Power Up**:
```bash
pip install -r requirements.txt
```

3. **Launch**:
```bash
python app.py
```

4. **Start Translating**: Visit http://127.0.0.1:5000 and watch the magic happen! 🎉

### 🧰 Essential Tools
- 🛠️ flask==2.0.1
- 🔧 werkzeug==2.0.3
- 📚 pdfplumber==0.10.2
- 🔍 langdetect==1.0.9
- 🌐 ollama==0.1.0

## 📖 How to Use

1. 🚀 Fire up the server: `python app.py`
2. 🌐 Open your favorite browser
3. 📂 Drop in your Chinese PDF
4. ⚡ Hit that "Upload & Translate" button
5. 🎉 Voilà! Your English translation is ready

## 🆘 Troubleshooting

- 🚫 **Translation Not Working?** Double-check if your PDF speaks Chinese!
- 🔄 **System Acting Up?** Try the old "turn it off and on again" trick
- 💾 **Download Issues?** Make sure your browser isn't blocking pop-ups

## 📜 License

Released under the MIT License - go wild! Just remember to share the love! 💖

## 🤝 Join the Fun!

Got ideas? Found a bug? Want to make this even more awesome? We'd love to have you on board! Drop by our GitHub repository and:
- 🌟 Star the project
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

Let's make translation amazing together! 🚀✨

---
*Built with ❤️ by Sreeraman*
