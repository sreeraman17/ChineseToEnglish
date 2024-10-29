# 🌏 Chinese to English PDF Translator 🚀

> Transform your Chinese PDFs into English with just a few clicks! ✨


## 📑 Table of Contents
- [What's This All About?](#-whats-this-all-about)
- [Key Features](#-key-features)
- [System Requirements](#-system-requirements)
- [Installation & Setup](#-installation--setup)
  - [Prerequisites](#prerequisites)
  - [Quick Start](#quick-start)
  - [Ollama Setup](#-ollama-setup)
  - [Docker Setup](#-docker-setup)
  - [Environment Configuration](#-environment-configuration)
- [Frontend Implementation](#-frontend-implementation)
- [Backend Implementation](#-backend-implementation)
- [API Documentation](#-api-documentation)
- [Usage Guide](#-how-to-use)
- [Performance Optimization](#-performance-optimization)
- [Monitoring](#-monitoring)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-join-the-fun)
- [License](#-license)

## 🎯 What's This All About?
A comprehensive web application that provides high-quality Chinese to English translation using the Qwen 2.5 model. With a sleek web interface that's as easy as drag-and-drop.

![Screenshot of the Chinese to English PDF Translator](https://github.com/sreeraman17/ChineseToEnglish/blob/main/screenshot.jpg)

Watch a demo video here https://www.loom.com/share/d580901a8f174d4b91880a17a217af21?sid=83d60034-1d48-444b-a77a-16721e4fdb08

## ✨ Key Features
- 🎭 **Drag & Drop**: Toss your PDFs into our translator like a boss
- 📊 **Live Progress Tracking**: Watch your translation come to life in real-time
- 💫 **Smart Text Panels**: Edit both Chinese and English text on the fly
- 📋 **Copy with Style**: One-click copying for both languages
- 💾 **Download & Go**: Save your translations instantly
- 🔔 **Smart Notifications**: Progress tracking with visual feedback
- 🚀 **High-Quality Translation**: Powered by Qwen 2.5 model
- 💾 **Smart Caching**: Improved performance for repeated content
- 📝 **Document Optimization**: Special handling for formal texts
- 📋 **Support files**: Check Input files for sample Chinese and English Documents (under Supporting files.zip)

## 💻 System Requirements
- 🖥️ **CPU**: 8+ cores recommended
- 🧠 **RAM**: Minimum 16GB, 32GB recommended
- 💽 **Storage**: 20GB+ free space
- 🏃 **OS**: Windows 10/11, macOS 12+, or Linux with kernel 5.4+

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Docker (needed for Ollama OpenUI)


### 🚀 Quick Start
```bash
# Clone the repository
git clone https://github.com/sreeraman17/ChineseToEnglish
cd ChineseToEnglish

# Install dependencies
pip install -r requirements.txt
```

### 🐋 Ollama Setup

#### Local Installation
```bash
# macOS (using Homebrew)
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download/windows

# Start Ollama service
ollama serve

# Pull Qwen model
ollama pull qwen2.5:7b
```

### 🐳 Docker Setup
```bash
# Create Ollama directory
mkdir ollama && cd ollama

# Create docker-compose.yml
cat << EOF > docker-compose.yml
version: '3.8'
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
volumes:
  ollama_data:
EOF

# Start container
docker-compose up -d

# Pull model in container
docker exec -it ollama bash -c "ollama pull qwen2.5:7b"
```

### ⚙️ Environment Configuration
```bash
# Create .env file
cat << EOF > .env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=300
EOF
```

## 🔧 Performance Optimization

### Docker Resources
```yaml
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 32G
        reservations:
          memory: 16G
```

### Model Configuration
```bash
# Optimize model settings
ollama pull qwen2.5:7b \
  --compute-dtype float16 \
  --max-parallel-loading 4
```

## 📊 Monitoring
```bash
# Monitor CPU and Memory
docker stats ollama

# Monitor GPU (if applicable)
nvidia-smi -l 1
```

## 🆘 Troubleshooting

### 🐳 Docker Issues
```bash
# Reset container
docker-compose down
docker volume rm ollama_data
docker-compose up -d

# Check GPU
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### 🤖 Model Issues
```bash
# Reset model
ollama rm qwen2.5:7b
ollama pull qwen2.5:7b --force
```

### 🔑 Permission Issues
```bash
# Fix Linux permissions
sudo chown -R $USER:$USER ~/.ollama
```

[... rest of the original README content ...]

## 🤝 Join the Fun!
Got ideas? Found a bug? Want to make this even more awesome? We'd love to have you on board! Drop by our GitHub repository and:
- 🌟 Star the project
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

## 📜 License
Released under the MIT License - go wild! Just remember to share the love! 💖

---
*Built with ❤️ by Sreeraman*
