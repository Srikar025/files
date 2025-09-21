# 🎨 Kolam Art Studio

A comprehensive Streamlit application that combines traditional Indian Kolam art with modern AI technology using Google's Gemini API.

## 🌟 Features

### 🎲 Kolam Generator
- Generate beautiful Kolam patterns using mathematical algorithms
- Multiple pattern types: symmetric, rotational, spiral, floral, and geometric
- Adjustable grid sizes (3x3 to 11x11)
- Real-time pattern visualization

### 📷 Upload & Recognition
- Upload Kolam images for AI-powered analysis
- Pattern classification (dot-grid based, freehand, symmetric)
- Symmetry analysis and mathematical property detection
- Computer vision analysis using OpenCV

### ✏️ Interactive Editor
- Create custom Kolam designs with interactive canvas
- Drag-and-drop dot placement
- Line and curve drawing tools
- Save and load designs in JSON format
- Export to PNG, SVG, or JSON

### 🤖 AI Analysis with Gemini
- Comprehensive pattern analysis using Google's Gemini API
- Cultural significance identification
- Design suggestions based on preferences
- Educational content about Kolam traditions
- Advanced mathematical pattern recognition

### 📚 Educational Content
- Learn about Kolam history and traditions
- Understand mathematical principles
- Explore regional variations
- Discover cultural significance

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key (free tier available)

### Installation

#### 🌐 Streamlit Cloud Deployment (Recommended)

1. **Fork or clone this repository to your GitHub account**

2. **Deploy to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Deploy with `main.py` as the main file

3. **Configure API Key in deployed app:**
   - Go to Settings page in your deployed app
   - Enter your Gemini API key
   - Click "Save API Key"

4. **Get Gemini API Key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the generated key

#### 💻 Local Development

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Gemini API Key:**
   
   **Option 1: Environment Variable (Recommended)**
   
   **Windows (PowerShell):**
   ```powershell
   $env:GEMINI_API_KEY="your_api_key_here"
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   set GEMINI_API_KEY=your_api_key_here
   ```
   
   **Linux/Mac:**
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```
   
   **Option 2: Manual Entry**
   - Run the app and go to Settings
   - Enter your API key manually

4. **Run the application:**
   ```bash
   streamlit run main.py
   ```

#### 🔧 Alternative: Use the launcher script
   ```bash
   python run_app.py
   ```

## 📁 Project Structure

```
kolam-art-studio/
├── main.py                 # Main Streamlit application
├── kolam_generator.py      # Pattern generation algorithms
├── kolam_recognition.py    # Image analysis and recognition
├── kolam_editor.py         # Interactive design editor
├── gemini_integration.py   # Gemini API integration
├── config.py              # Configuration and API key management
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🎯 Usage Guide

### 1. Kolam Generator
- Select grid size and pattern type
- Click "Generate Kolam" to create patterns
- Explore different mathematical algorithms

### 2. Upload & Recognition
- Upload Kolam images (PNG, JPG, JPEG)
- Choose between basic analysis or AI-powered analysis
- View pattern classification and symmetry scores

### 3. Interactive Editor
- Use drawing tools to create custom designs
- Place dots and connect them with lines
- Save your designs and export in various formats

### 4. AI Analysis
- Upload images for comprehensive AI analysis
- Get design suggestions based on preferences
- Learn about mathematical properties and cultural significance

### 5. Learning Center
- Explore educational content about Kolam traditions
- Learn about history, techniques, and cultural significance
- Understand mathematical principles behind the art

## 🔧 Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Google Generative AI**: Gemini API integration
- **Pillow**: Image processing
- **NumPy**: Numerical computations
- **Matplotlib**: Pattern visualization
- **OpenCV**: Computer vision analysis
- **Plotly**: Interactive visualizations

### API Features
- **Free Tier**: Gemini API offers free usage with rate limits
- **Image Analysis**: Advanced pattern recognition and classification
- **Text Generation**: Educational content and design suggestions
- **Multi-modal**: Combined text and image processing

## 🎨 Pattern Types

### Basic Symmetric
Simple symmetric patterns with alternating dot placement

### Rotational
Patterns with rotational symmetry around a center point

### Spiral
Spiral patterns following mathematical curves

### Floral
Floral designs with petal-like arrangements

### Geometric
Geometric shapes and structured patterns

## 🔍 Analysis Features

### Pattern Classification
- Dot-grid based Kolam
- Freehand designs
- Symmetric patterns
- Mixed styles

### Symmetry Analysis
- Rotational symmetry detection
- Reflectional symmetry analysis
- Symmetry quality scoring

### Mathematical Properties
- Grid structure analysis
- Geometric pattern recognition
- Fractal and recursive pattern detection

## 🌐 Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📞 Support

For support or questions:
- Check the Settings page for API key configuration
- Review the educational content for Kolam background
- Explore the different features to understand functionality

## 🚀 Deployment

### Streamlit Cloud (Recommended)
- **Easy deployment**: Connect your GitHub repo to Streamlit Cloud
- **Free hosting**: No server management required
- **Automatic updates**: Push to GitHub to update your app
- **Custom domain**: Option to use your own domain

### Other Platforms
- **Heroku**: Use the included `Procfile`
- **Docker**: Build and deploy using Docker containers
- **AWS/GCP/Azure**: Deploy as a containerized application

### Configuration for Cloud Deployment
- Use Streamlit secrets for API keys in production
- Configure environment variables for different environments
- Set up monitoring and logging for production use

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 🔄 Updates

Regular updates include:
- New pattern generation algorithms
- Enhanced AI analysis capabilities
- Improved user interface
- Additional educational content

## 📄 Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
- [API Documentation](docs/api.md) - API reference (coming soon)
- [User Guide](docs/user-guide.md) - Comprehensive user manual (coming soon)

---

**Enjoy exploring the beautiful world of Kolam art with AI! 🎨✨**
