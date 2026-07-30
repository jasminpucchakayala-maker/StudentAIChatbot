import os
from pathlib import Path

# Paths Setup
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
STYLES_DIR = BASE_DIR / "styles"
UTILS_DIR = BASE_DIR / "utils"

INTENTS_FILE = BASE_DIR / "intents.json"
HISTORY_FILE = BASE_DIR / "chatbot_history.csv"

# Ensure essential folders exist
for folder in [ASSETS_DIR, STYLES_DIR, UTILS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Application Meta
APP_TITLE = "CHINGU AI"
APP_SUBTITLE = "Your Smart Academic Copilot"
APP_VERSION = "v2.1.0-Beta"
DEVELOPER = "Antigravity Dev Team & Student Intern"
LICENSE = "MIT License"

# Matching Thresholds
MATCH_THRESHOLD = 0.55       # Above this: confident answer
SUGGESTION_THRESHOLD = 0.35  # Between this and MATCH_THRESHOLD: returns answer with warning, or suggests intents
MIN_CONFIDENCE = 0.20        # Below this: fallback action occurs

# Conversational fallbacks
FALLBACK_RESPONSES = [
    "I'm sorry, I couldn't find a precise match for that dynamic query. Could you rephrase your question?",
    "I'm still learning! I don't have enough confidence in my training data to answer that. Try asking about admissions, courses, or hostel facilities.",
    "That seems outside my current knowledge base. You can scroll through the FAQ categories in the sidebar or retype your query with keywords like 'fees', 'placements', or 'exams'.",
    "I'm not quite sure how to answer that. Feel free to contact our support desk or check the contact details in the suggestions!"
]

RANDOM_GREETINGS = [
    "Hello! How can I assist you with your academic queries today?",
    "Hi there! Welcome to CHINGU AI. What information are you looking for today?",
    "Greetings! I'm here to help you navigate college admissions, fees, hostel queries, and more. How can I help?",
    "Hey! Ask me anything about course structures, sports facilities, anti-ragging, or placements!"
]

RANDOM_FAREWELLS = [
    "Goodbye! Wishing you the best in your academic journey.",
    "Have a great day! Don't hesitate to reach out if you have more questions.",
    "Bye! Stay curious and study hard!",
    "Farewell! Remember, I'm always here to help you with college queries."
]

RANDOM_THANKS = [
    "You are very welcome! Let me know if you need anything else.",
    "Happy to help! Academic success is just a query away.",
    "My pleasure! Feel free to ask more queries.",
    "Glad I could clarify that for you! Have a great day ahead."
]

# Quick Suggested Questions
SUGGESTED_QUESTIONS = [
    "What are the admission requirements?",
    "What courses are offered here?",
    "Show me the fee structure.",
    "What scholarships are available?",
    "Tell me about college placements.",
    "How do I join the Hostel?",
    "Where is the campus located?"
]

# Dashboard Setup Defaults
PLOTLY_THEME = "plotly_dark"
THEME_PRIMARY_COLOR = "#0EA5E9"  # Cyan
THEME_SECONDARY_COLOR = "#0284C7" # Medium Blue
