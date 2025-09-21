import streamlit as st
import os
from PIL import Image
import io

# Import our custom modules
from kolam_generator import KolamGenerator, get_available_patterns
from kolam_recognition import KolamRecognizer, create_analysis_visualization
from kolam_editor import KolamEditor
from gemini_integration import GeminiKolamAnalyzer, display_gemini_analysis, create_learning_interface
from ai_kolam_generator import create_ai_generator_interface
from config import GEMINI_API_KEY, get_gemini_api_key

# Page configuration
st.set_page_config(
    page_title="Kolam Art Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .sub-header {
        color: #A23B72;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
    }
    .feature-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎨 Kolam Art Studio</h1>', unsafe_allow_html=True)
    st.markdown("### Discover, Create, and Analyze Traditional Indian Kolam Art with AI")
    
    # Sidebar navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Choose a feature:",
        [
            "🏠 Home",
            "🎲 Kolam Generator", 
            "🤖 AI Kolam Creator",
            "📷 Upload & Recognition",
            "✏️ Interactive Editor",
            "🧠 AI Analysis",
            "📚 Learn About Kolam",
            "⚙️ Settings"
        ]
    )
    
    # API Key status
    current_key = get_gemini_api_key()
    if current_key:
        st.sidebar.success("✅ Gemini API Connected")
    else:
        st.sidebar.warning("⚠️ Gemini API Key Required")
        st.sidebar.info("Configure API key in Settings to enable AI features")
    
    # Route to different pages
    if page == "🏠 Home":
        show_home_page()
    elif page == "🎲 Kolam Generator":
        show_generator_page()
    elif page == "🤖 AI Kolam Creator":
        show_ai_generator_page()
    elif page == "📷 Upload & Recognition":
        show_recognition_page()
    elif page == "✏️ Interactive Editor":
        show_editor_page()
    elif page == "🧠 AI Analysis":
        show_ai_analysis_page()
    elif page == "📚 Learn About Kolam":
        show_learning_page()
    elif page == "⚙️ Settings":
        show_settings_page()

def show_home_page():
    """Display the home page"""
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.write("""
    **Welcome to Kolam Art Studio!** 
    
    This application combines traditional Indian Kolam art with modern AI technology. 
    Explore the beauty of mathematical patterns, create your own designs, and learn 
    about the rich cultural heritage of Kolam art.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🎲 Kolam Generator")
        st.write("Generate beautiful Kolam patterns using mathematical algorithms. Choose from various pattern types including symmetric, rotational, spiral, and floral designs.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🤖 AI Kolam Creator")
        st.write("Describe your dream Kolam in words, and AI will generate it for you! Use natural language prompts to create unique patterns.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 📷 Upload & Recognition")
        st.write("Upload images of Kolam designs and use AI to analyze their patterns, symmetry, and cultural significance.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### ✏️ Interactive Editor")
        st.write("Create your own Kolam designs with our interactive canvas. Drag dots, draw connections, and experiment with different patterns.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🧠 AI Analysis")
        st.write("Get detailed AI-powered analysis of your Kolam designs using Google's Gemini API for pattern recognition and cultural insights.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 📚 Learn About Kolam")
        st.write("Discover the rich history, cultural significance, and mathematical principles behind traditional Kolam art.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick start guide
    st.markdown('<div class="sub-header">🚀 Quick Start Guide</div>', unsafe_allow_html=True)
    st.write("""
    1. **Start with Generator**: Try the Kolam Generator to see different pattern types
    2. **Try AI Creator**: Describe your dream Kolam and let AI generate it
    3. **Experiment with Editor**: Use the Interactive Editor to create your own designs
    4. **Upload & Analyze**: Upload Kolam images to get AI-powered analysis
    5. **Learn**: Explore the educational content about Kolam traditions
    6. **Settings**: Configure your API keys and preferences
    """)

def show_generator_page():
    """Display the Kolam generator page"""
    st.markdown('<div class="sub-header">🎲 Kolam Generator</div>', unsafe_allow_html=True)
    
    generator = KolamGenerator()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ Generator Settings")
        
        # Grid size selection
        grid_size = st.selectbox(
            "Grid Size:",
            options=[3, 5, 7, 9, 11],
            index=2,
            help="Choose the size of the dot grid"
        )
        
        # Pattern type selection
        pattern_types = get_available_patterns()
        pattern_type = st.selectbox(
            "Pattern Type:",
            options=pattern_types,
            index=0,
            help="Select the type of pattern to generate"
        )
        
        # Generate button
        if st.button("🎨 Generate Kolam", type="primary"):
            with st.spinner("Generating pattern..."):
                grid = generator.generate_pattern(grid_size, pattern_type)
                fig = generator.draw_kolam(grid, f"{pattern_type.replace('_', ' ').title()} Pattern")
                
                st.session_state.generated_kolam = {
                    'grid': grid,
                    'pattern_type': pattern_type,
                    'grid_size': grid_size,
                    'figure': fig
                }
    
    with col2:
        st.subheader("🎨 Generated Kolam")
        
        if 'generated_kolam' in st.session_state:
            kolam_data = st.session_state.generated_kolam
            st.pyplot(kolam_data['figure'])
            
            # Pattern information
            st.info(f"""
            **Pattern Type:** {kolam_data['pattern_type'].replace('_', ' ').title()}
            **Grid Size:** {kolam_data['grid_size']}x{kolam_data['grid_size']}
            **Dots:** {int(kolam_data['grid'].sum())}
            """)
        else:
            st.info("👆 Generate a Kolam pattern using the settings on the left!")
    
    # Pattern descriptions
    st.markdown('<div class="sub-header">📖 Pattern Types</div>', unsafe_allow_html=True)
    
    pattern_descriptions = {
        'basic_symmetric': 'Simple symmetric patterns with alternating dot placement',
        'rotational': 'Patterns with rotational symmetry around a center point',
        'spiral': 'Spiral patterns following mathematical curves',
        'floral': 'Floral designs with petal-like arrangements',
        'geometric': 'Geometric shapes and structured patterns'
    }
    
    for pattern, description in pattern_descriptions.items():
        st.write(f"**{pattern.replace('_', ' ').title()}:** {description}")

def show_ai_generator_page():
    """Display the AI Kolam generator page"""
    st.markdown('<div class="sub-header">🤖 AI Kolam Creator</div>', unsafe_allow_html=True)
    
    # Show the AI generator interface
    create_ai_generator_interface()

def show_recognition_page():
    """Display the upload and recognition page"""
    st.markdown('<div class="sub-header">📷 Upload & Recognition</div>', unsafe_allow_html=True)
    
    recognizer = KolamRecognizer()
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a Kolam image:",
        type=['png', 'jpg', 'jpeg'],
        help="Upload an image of a Kolam design for analysis"
    )
    
    if uploaded_file:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Kolam Image", use_column_width=True)
        
        # Analysis options
        col1, col2 = st.columns(2)
        
        with col1:
            analyze_basic = st.button("🔍 Basic Analysis", type="primary")
        
        with col2:
            analyze_ai = st.button("🤖 AI Analysis (Gemini)", type="secondary")
        
        if analyze_basic:
            with st.spinner("Analyzing image..."):
                analysis = recognizer.analyze_kolam_image(image)
                create_analysis_visualization(analysis)
        
        if analyze_ai and recognizer.model:
            with st.spinner("Running AI analysis with Gemini..."):
                ai_analysis = recognizer.model.generate_content([
                    "Analyze this Kolam image and provide detailed insights about its pattern, symmetry, and cultural significance.",
                    {"mime_type": uploaded_file.type, "data": uploaded_file.getvalue()}
                ])
                st.markdown("### 🤖 AI Analysis Results")
                st.write(ai_analysis.text)
        elif analyze_ai and not recognizer.model:
            st.error("Gemini API not configured. Please set your API key in Settings.")
    
    else:
        st.info("👆 Upload a Kolam image to get started with analysis!")

def show_editor_page():
    """Display the interactive editor page"""
    st.markdown('<div class="sub-header">✏️ Interactive Kolam Editor</div>', unsafe_allow_html=True)
    
    # Initialize editor
    if 'editor' not in st.session_state:
        st.session_state.editor = KolamEditor()
    
    editor = st.session_state.editor
    editor.create_editor_interface()

def show_ai_analysis_page():
    """Display the AI analysis page"""
    st.markdown('<div class="sub-header">🤖 AI Analysis with Gemini</div>', unsafe_allow_html=True)
    
    analyzer = GeminiKolamAnalyzer()
    
    if not analyzer.model:
        st.warning("⚠️ Gemini API not configured. Please set your API key in Settings.")
        return
    
    # Analysis options
    tab1, tab2, tab3 = st.tabs(["📊 Design Analysis", "💡 Suggestions", "🎯 Pattern Recognition"])
    
    with tab1:
        st.subheader("Analyze Your Design")
        
        # Upload image for analysis
        uploaded_image = st.file_uploader(
            "Upload Kolam image for detailed AI analysis:",
            type=['png', 'jpg', 'jpeg'],
            key="ai_analysis_upload"
        )
        
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="Image for AI Analysis", width=300)
            
            if st.button("🚀 Run Comprehensive Analysis"):
                with st.spinner("Running comprehensive AI analysis..."):
                    analysis = analyzer.analyze_uploaded_kolam(image)
                    display_gemini_analysis(analysis)
    
    with tab2:
        st.subheader("Get Design Suggestions")
        
        # User preferences
        col1, col2 = st.columns(2)
        
        with col1:
            complexity = st.selectbox("Preferred Complexity:", ["Simple", "Medium", "Complex"])
            symmetry = st.selectbox("Symmetry Type:", ["Rotational", "Reflectional", "Both", "None"])
        
        with col2:
            style = st.selectbox("Style Preference:", ["Traditional", "Modern", "Geometric", "Floral"])
            grid_size = st.selectbox("Grid Size:", [3, 5, 7, 9, 11])
        
        if st.button("💡 Get Suggestions"):
            preferences = {
                "complexity": complexity,
                "symmetry": symmetry,
                "style": style,
                "grid_size": grid_size
            }
            
            with st.spinner("Generating suggestions..."):
                suggestions = analyzer.generate_kolam_suggestions(preferences)
                
                for i, suggestion in enumerate(suggestions, 1):
                    st.markdown(f"### Suggestion {i}")
                    st.write(suggestion)
                    st.divider()
    
    with tab3:
        st.subheader("Advanced Pattern Recognition")
        st.info("Upload a Kolam image to get advanced pattern recognition and mathematical analysis.")

def show_learning_page():
    """Display the learning page"""
    st.markdown('<div class="sub-header">📚 Learn About Kolam Tradition</div>', unsafe_allow_html=True)
    
    analyzer = GeminiKolamAnalyzer()
    create_learning_interface(analyzer)

def show_settings_page():
    """Display the settings page"""
    st.markdown('<div class="sub-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    # API Configuration
    st.subheader("🔑 API Configuration")
    
    # Check current API key status
    current_api_key = get_gemini_api_key()
    api_key_source = "Unknown"
    
    # Determine source of API key
    try:
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            api_key_source = "Streamlit Secrets (Cloud)"
        elif 'gemini_api_key' in st.session_state and st.session_state['gemini_api_key']:
            api_key_source = "Session State (App)"
        elif os.getenv('GEMINI_API_KEY'):
            api_key_source = "Environment Variable (Local)"
    except:
        pass
    
    if current_api_key:
        st.success("✅ Gemini API Key is configured")
        st.info(f"Source: {api_key_source}")
        
        # Show masked API key
        masked_key = current_api_key[:8] + "..." + current_api_key[-4:] if len(current_api_key) > 12 else "***"
        st.code(f"API Key: {masked_key}")
        
        # Option to update API key
        if st.button("🔄 Update API Key"):
            st.session_state['show_api_input'] = True
        
        if st.button("🗑️ Clear API Key"):
            if 'gemini_api_key' in st.session_state:
                del st.session_state['gemini_api_key']
            st.rerun()
    else:
        st.warning("⚠️ Gemini API Key not found")
        st.session_state['show_api_input'] = True
    
    # API key input section
    if st.session_state.get('show_api_input', False):
        st.subheader("🔑 Enter API Key")
        
        api_key = st.text_input(
            "Gemini API Key:",
            type="password",
            help="Get your API key from Google AI Studio",
            placeholder="Enter your Gemini API key here..."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save API Key", type="primary"):
                if api_key:
                    st.session_state['gemini_api_key'] = api_key
                    st.session_state['show_api_input'] = False
                    st.success("✅ API key saved successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a valid API key")
        
        with col2:
            if st.button("❌ Cancel"):
                st.session_state['show_api_input'] = False
                st.rerun()
    
    # Instructions
    st.subheader("📖 Setup Instructions")
    
    # Tabs for different deployment scenarios
    tab1, tab2, tab3 = st.tabs(["🌐 Streamlit Cloud", "💻 Local Development", "🔧 Manual Setup"])
    
    with tab1:
        st.markdown("""
        ### 🌐 For Streamlit Cloud Deployment:
        
        **Option 1: Use App Settings (Recommended)**
        1. Enter your API key in the field above
        2. Click "Save API Key"
        3. Your key will be stored in the app session
        
        **Option 2: Use Streamlit Secrets**
        1. In your Streamlit Cloud dashboard, go to "Settings"
        2. Add a new secret with key: `GEMINI_API_KEY`
        3. Set value to your API key
        4. Redeploy your app
        
        **Getting Your API Key:**
        1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Sign in with your Google account
        3. Click "Create API Key"
        4. Copy the generated key
        """)
    
    with tab2:
        st.markdown("""
        ### 💻 For Local Development:
        
        **Environment Variable (Recommended):**
        
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
        
        **Using .env file:**
        1. Create a `.env` file in your project root
        2. Add: `GEMINI_API_KEY=your_api_key_here`
        3. The app will automatically load it
        """)
    
    with tab3:
        st.markdown("""
        ### 🔧 Manual Configuration:
        
        **Using App Settings:**
        1. Enter your API key in the field above
        2. Click "Save API Key"
        3. The key will be stored for your session
        
        **Features Requiring API Key:**
        - 🤖 AI Analysis
        - 📷 Advanced Image Recognition  
        - 💡 Design Suggestions
        - 📚 Educational Content
        
        **Security Note:**
        - API keys stored in session state are temporary
        - For permanent storage, use environment variables or Streamlit secrets
        - Never share your API key publicly
        """)
    
    # App Information
    st.subheader("ℹ️ App Information")
    st.info("""
    **Kolam Art Studio** v1.0
    
    Features:
    - Traditional Kolam pattern generation
    - AI-powered image analysis
    - Interactive design editor
    - Educational content about Kolam traditions
    
    Built with Streamlit and Google Gemini AI
    """)

if __name__ == "__main__":
    main()
