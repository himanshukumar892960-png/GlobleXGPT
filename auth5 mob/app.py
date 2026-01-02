from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from gemini_client import GeminiClient
from openrouter_client import OpenRouterClient
from system_control import SystemControl
from weather_service import WeatherService
from news_service import NewsService
from imagen_client import ImagenClient
from stability_client import StabilityClient
from crypto_service import CryptoService
from stock_service import StockService
from runway_client import RunwayClient
from youtube_service import YouTubeService
import os

from dotenv import load_dotenv
import os

load_dotenv()

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Add file handler
file_handler = logging.FileHandler('auth_debug.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = Flask(__name__)
CORS(app)

# Load API key from environment variable
API_KEY = os.getenv("GEMINI_API_KEY") 
if not API_KEY:
    print("Warning: GEMINI_API_KEY not found in .env file.")

# Load Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Error initializing Supabase: {e}")
else:
    print("Warning: SUPABASE_URL or SUPABASE_KEY not found in .env file.")

gemini = GeminiClient(API_KEY)
system = SystemControl()
weather = WeatherService(os.getenv("OPENWEATHER_API_KEY"))
news = NewsService(os.getenv("NEWS_API_KEY"))
crypto = CryptoService(os.getenv("CMC_API_KEY"))
stock = StockService(os.getenv("ALPHA_VANTAGE_API_KEY"))
youtube = YouTubeService(os.getenv("YOUTUBE_API_KEY"))

# Initialize AI Assistant
OR_API_KEY = os.getenv("OPENROUTER_API_KEY")
OR_MODEL = os.getenv("OPENROUTER_MODEL")

if OR_API_KEY:
    ai_assistant = OpenRouterClient(OR_API_KEY, OR_MODEL)
    logger.info(f"Using OpenRouter AI: {OR_MODEL}")
else:
    ai_assistant = GeminiClient(API_KEY)
    logger.info("Using Gemini AI")

# Initialize Image Assistant
IMAGEN_API_KEY = os.getenv("IMAGEN_API_KEY")
IMAGEN_MODEL = os.getenv("IMAGEN_MODEL")
imagen_assistant = None

if IMAGEN_API_KEY:
    imagen_assistant = ImagenClient(IMAGEN_API_KEY, IMAGEN_MODEL)
    logger.info(f"Image generation enabled with model: {IMAGEN_MODEL}")

# Initialize Stability Assistant
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_MODEL = os.getenv("STABILITY_MODEL")
stability_assistant = None

if STABILITY_API_KEY:
    stability_assistant = StabilityClient(STABILITY_API_KEY, STABILITY_MODEL)
    logger.info(f"Stability AI enabled with model: {STABILITY_MODEL}")

# Initialize Runway Assistant
RUNWAYML_API_KEY = os.getenv("RUNWAYML_API_KEY")
runway_assistant = None

if RUNWAYML_API_KEY:
    runway_assistant = RunwayClient(RUNWAYML_API_KEY)
    logger.info("RunwayML Video AI enabled")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    
    data = request.json
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name', '')
    avatar_url = data.get('avatar_url', '')
    
    try:
        response = supabase.auth.sign_up({
            "email": email, 
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "avatar_url": avatar_url
                }
            }
        })
        # Check if user was created
        if response.user:
            return jsonify({"message": "Sign up successful. Please check your email for verification.", "user_id": response.user.id}), 200
        else:
            return jsonify({"error": "Sign up failed"}), 400
    except Exception as e:
        error_msg = str(e)
        logger.error(f"SIGNUP ERROR: {error_msg}")
        
        if "Database error saving new user" in error_msg:
             return jsonify({
                 "error": "Supabase Configuration Error: You are missing the 'profiles' table or have a broken trigger. Please run the 'setup_database.sql' script in your Supabase SQL Editor."
             }), 500
             
        return jsonify({"error": error_msg}), 400

@app.route('/login', methods=['POST'])
def login():
    if not supabase:
        logger.error("LOGIN ERROR: Supabase not configured")
        return jsonify({"error": "Supabase not configured"}), 500

    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    logger.info(f"Attempting login for: {email}") # Log the email attempt
    
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.session:
            logger.info("Login successful")
            
            # Extract metadata
            user_metadata = response.user.user_metadata or {}
            full_name = user_metadata.get('full_name', '')
            avatar_url = user_metadata.get('avatar_url', '')
            
            return jsonify({
                "message": "Login successful", 
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "full_name": full_name,
                    "avatar_url": avatar_url
                }
            }), 200
        else:
             logger.warning("Login failed: No session returned")
             return jsonify({"error": "Login failed"}), 401
    except Exception as e:
        logger.error(f"LOGIN ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500

    data = request.json
    user_id = data.get('user_id')
    avatar_url = data.get('avatar_url')
    full_name = data.get('full_name')
    
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
        
    try:
        update_data = {}
        if avatar_url:
            update_data["avatar_url"] = avatar_url
        if full_name:
            update_data["full_name"] = full_name

        if not update_data:
            return jsonify({"error": "No data to update"}), 400

        # Update user metadata via admin API (assuming server key has permissions)
        supabase.auth.admin.update_user_by_id(user_id, {"user_metadata": update_data})
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        logger.error(f"UPDATE PROFILE ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_input = data.get('prompt')
    
    # Check for system commands first (conceptual)
    if "screenshot" in user_input.lower():
        system.take_screenshot()
        return jsonify({"response": "Screenshot taken successfully.", "emotion": "Neutral"})
    elif "camera" in user_input.lower() or "photo" in user_input.lower():
        system.capture_camera()
        return jsonify({"response": "Camera image captured.", "emotion": "Neutral"})
    elif "open" in user_input.lower():
        app_name = user_input.lower().split("open")[-1].strip()
        response_text = system.open_app(app_name)
        return jsonify({"response": response_text, "emotion": "Neutral"})
    elif "weather" in user_input.lower():
        # Try to extract city name
        words = user_input.lower().split()
        city = "London" # Default
        if "in" in words:
            try:
                city = user_input.lower().split("in")[-1].strip().strip('?').strip('.')
            except:
                pass
        elif "for" in words:
            try:
                city = user_input.lower().split("for")[-1].strip().strip('?').strip('.')
            except:
                pass
        
        weather_info = weather.get_weather(city)
        return jsonify({"response": weather_info, "emotion": "Neutral"})
    elif "news" in user_input.lower():
        news_info = news.get_top_news()
        return jsonify({"response": news_info, "emotion": "Neutral"})
    elif "price of" in user_input.lower() or "price for" in user_input.lower():
        # Try to extract crypto symbol
        words = user_input.lower().split()
        symbol = None
        if "of" in words:
            symbol = words[words.index("of") + 1].strip("?").strip(".")
        elif "for" in words:
            symbol = words[words.index("for") + 1].strip("?").strip(".")
        
        if symbol:
            # Map common names to symbols
            mapping = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL", "dogecoin": "DOGE", "cardano": "ADA"}
            symbol = mapping.get(symbol, symbol)
            
            crypto_info = crypto.get_price(symbol)
            return jsonify({"response": crypto_info, "emotion": "Neutral"})
    elif "crypto" in user_input.lower() or "cryptocurrency" in user_input.lower():
         top_cryptos = crypto.get_top_cryptos()
         return jsonify({"response": top_cryptos, "emotion": "Neutral"})
    elif "stock" in user_input.lower() or "share price" in user_input.lower():
        # Try to extract stock symbol
        words = user_input.lower().split()
        symbol = None
        if "of" in words:
            symbol = words[words.index("of") + 1].strip("?").strip(".")
        elif "for" in words:
            symbol = words[words.index("for") + 1].strip("?").strip(".")
        elif words:
            # Fallback to last word if it looks like a ticker (e.g. "Price of aapl")
            # But the logic above already handles "of" and "for"
            pass
        
        if symbol:
            stock_info = stock.get_stock_price(symbol)
            return jsonify({"response": stock_info, "emotion": "Neutral"})
        else:
            news_info = stock.get_market_news()
            return jsonify({"response": news_info, "emotion": "Neutral"})
    
    elif "youtube" in user_input.lower():
        if "trending" in user_input.lower() or "popular" in user_input.lower():
            trending = youtube.get_trending_videos()
            return jsonify({"response": trending, "emotion": "Happy"})
        
        # Extract search query
        query = user_input.lower().replace("youtube", "").replace("search", "").replace("find", "").strip()
        if not query:
            return jsonify({"response": "What would you like to search for on YouTube?", "emotion": "Neutral"})
        
        results = youtube.search_videos(query)
        return jsonify({"response": results, "emotion": "Happy"})
    
    elif "generate" in user_input.lower() and "image" in user_input.lower():
        active_image_assistant = stability_assistant or imagen_assistant
        
        if not active_image_assistant:
            return jsonify({"response": "Image generation is not configured. Please add an API key.", "emotion": "Neutral"})
        
        # Extract prompt
        prompt = user_input.lower().replace("generate", "").replace("an", "").replace("image", "").replace("of", "").strip()
        if not prompt:
             return jsonify({"response": "Please provide a description for the image.", "emotion": "Neutral"})
        
        image_data = active_image_assistant.generate_image(prompt)
        if image_data:
            return jsonify({
                "response": f"I've generated that image for you! ![Generated Image]({image_data})",
                "emotion": "Happy",
                "image_data": image_data
            })
        else:
            return jsonify({"response": "I'm sorry, I couldn't generate that image right now.", "emotion": "Sad"})
    
    # Image Generation
    elif any(word in user_input.lower() for word in ["generate image", "create image", "make image", "draw", "paint"]):
        active_image_assistant = stability_assistant or imagen_assistant
        
        if not active_image_assistant:
            return jsonify({"response": "Image generation is not configured. Please add an API key.", "emotion": "Neutral"})
        
        # Extract prompt - remove trigger words
        prompt = user_input.lower()
        for word in ["generate", "create", "make", "an", "image", "of", "draw", "paint", "me"]:
            prompt = prompt.replace(word, "")
        prompt = prompt.strip()
        
        if not prompt:
             return jsonify({"response": "Please provide a description for the image.", "emotion": "Neutral"})
        
        image_data = active_image_assistant.generate_image(prompt)
        if image_data:
            return jsonify({
                "response": f"I've generated that image for you! ![Generated Image]({image_data})",
                "emotion": "Happy",
                "image_data": image_data
            })
        else:
            return jsonify({"response": "I'm sorry, I couldn't generate that image right now.", "emotion": "Sad"})
    
    # Video Generation
    elif any(word in user_input.lower() for word in ["generate video", "create video", "make video", "animate"]):
        if not runway_assistant:
            return jsonify({"response": "Video generation is not configured. Please add a RunwayML API key.", "emotion": "Neutral"})
        
        # Extract prompt
        prompt = user_input.lower()
        for word in ["generate", "create", "make", "a", "video", "of", "animate", "me"]:
            prompt = prompt.replace(word, "")
        prompt = prompt.strip()
        
        if not prompt:
            prompt = "Animate this image" if data.get('file') else "A cinematic scene"
            
        file_data = data.get('file')
        image_url = None
        if file_data and file_data.get('type', '').startswith('image/'):
            image_url = file_data.get('data') # This is the base64 data URL
        
        # If it's just 'animate' and there's a file, but no text, prompt might be empty
        video_url = runway_assistant.generate_video(prompt, image_url=image_url)
        if video_url:
            return jsonify({
                "response": f"I've generated that video for you! \n\n<video controls width='100%' style='border-radius:10px; margin-top:10px;'><source src='{video_url}' type='video/mp4'>Your browser does not support the video tag.</video>",
                "emotion": "Happy",
                "video_url": video_url
            })
        else:
            return jsonify({"response": "I'm sorry, I couldn't generate that video right now. It might take a few minutes or there might be an issue with the service.", "emotion": "Sad"})

    # Get combined response and emotion in ONE call
    file_data = data.get('file')
    result = ai_assistant.get_full_response(user_input, file_data=file_data)
    
    return jsonify({
        "response": result["response"],
        "emotion": result["emotion"]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
