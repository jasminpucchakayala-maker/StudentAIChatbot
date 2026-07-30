import sys
import difflib
from utils.text_processing import preprocess_text, clean_text

# Safe Fuzzy string matching import
try:
    from rapidfuzz import fuzz
except ImportError:
    try:
        from fuzzywuzzy import fuzz
    except ImportError:
        fuzz = None

def get_string_similarity(str1: str, str2: str) -> float:
    """Calculate character-level similarity between two raw strings."""
    c_str1 = clean_text(str1)
    c_str2 = clean_text(str2)
    if not c_str1 or not c_str2:
        return 0.0
    
    if fuzz:
        try:
            # We use token_sort_ratio which is excellent at ignores word order differences
            return float(fuzz.token_sort_ratio(c_str1, c_str2) / 100.0)
        except Exception:
            pass
            
    # Fallback to difflib
    return float(difflib.SequenceMatcher(None, c_str1, c_str2).ratio())

def get_token_similarity(tokens1: list, tokens2: list) -> float:
    """Calculate token overlap Jaccard and Overlap coefficients."""
    if not tokens1 or not tokens2:
        return 0.0
    
    set1, set2 = set(tokens1), set(tokens2)
    intersection = set1.intersection(set2)
    
    if not intersection:
        return 0.0
        
    jaccard = len(intersection) / len(set1.union(set2))
    
    # Overlap Coefficient (size of intersection divided by size of the smaller set)
    # This prevents penalizing longer patterns matching short inputs.
    overlap = len(intersection) / min(len(set1), len(set2))
    
    # Return weighted average
    return 0.4 * jaccard + 0.6 * overlap

def calculate_confidence(user_query: str, pattern: str) -> float:
    """Get the hybrid similarity score combining character & token similarities."""
    # 1. Character/Word-order similarity
    str_sim = get_string_similarity(user_query, pattern)
    
    # 2. Token overlap similarity after lemmatization and stopword removal
    user_tokens = preprocess_text(user_query)
    pattern_tokens = preprocess_text(pattern)
    token_sim = get_token_similarity(user_tokens, pattern_tokens)
    
    # Hybrid Score (60% token structural match + 40% character spelling match)
    if len(user_tokens) == 0:
        return str_sim
        
    hybrid_score = 0.4 * str_sim + 0.6 * token_sim
    return round(hybrid_score, 4)

def find_best_intent(user_query: str, intents_data: list) -> dict:
    """
    Search all patterns in all intents to find the closest match.
    Returns:
        dict: {
            'tag': str, 
            'confidence': float, 
            'matched_pattern': str, 
            'responses': list, 
            'suggestions': list
        }
    """
    best_match = {
        "tag": "unknown",
        "confidence": 0.0,
        "matched_pattern": None,
        "responses": [],
        "suggestions": []
    }
    
    clean_query = clean_text(user_query)
    if not clean_query:
        return best_match

    max_confidence = 0.0
    matched_intent = None
    matched_pattern = None
    
    # Search loop
    for intent in intents_data:
        for pattern in intent.get("patterns", []):
            confidence = calculate_confidence(clean_query, pattern)
            
            # Exact match boost
            if clean_query == clean_text(pattern):
                confidence = 1.0
                
            if confidence > max_confidence:
                max_confidence = confidence
                matched_intent = intent
                matched_pattern = pattern
                
    if matched_intent and max_confidence > 0.0:
        best_match.update({
            "tag": matched_intent.get("tag", "unknown"),
            "confidence": max_confidence,
            "matched_pattern": matched_pattern,
            "responses": matched_intent.get("responses", []),
            "suggestions": matched_intent.get("suggestions", [])
        })
        
    return best_match

def detect_conversational_intent(user_query: str) -> str:
    """
    Check for quick conversational triggers like greetings, farewells, thanks, identity, and help.
    Returns the keyword tag of the conversational trigger config if matched, else None.
    """
    query = clean_text(user_query)
    if not query:
        return None
        
    # GREETINGS
    greetings = {
        "hello", "hi", "hey", "greetings", "good morning", "good afternoon", 
        "good evening", "howdy", "whats up", "sup", "yo", "hola"
    }
    # GOODBYES
    goodbyes = {
        "bye", "goodbye", "see you", "farewell", "quit", "exit", 
        "talk to you later", "take care", "adios"
    }
    # THANKS
    thanks = {
        "thank you", "thanks", "thank you so much", "thank", "much appreciated", 
        "thanks a lot", "great help", "thankful", "grateful"
    }
    # IDENTITY
    identity = {
        "who are you", "what is your name", "tell me about yourself", 
        "your name", "who built you", "what do you do", "are you an ai", 
        "who is the developers", "who created you", "who designed you"
    }
    # HELP
    help_triggers = {
        "help", "how to use", "what card suggestions", "show menu", 
        "give help", "help commands", "features list", "what can you do"
    }
    
    # Fast exact checks or word overlaps
    words = set(query.split())
    
    if query in greetings or any(w in greetings for w in words):
        return "greeting"
    if query in goodbyes or any(w in goodbyes for w in words):
        return "goodbye"
    if query in thanks or any(w in thanks for w in words):
        return "thanks"
    if query in identity or any(query.startswith(i) for i in identity):
        return "identity"
    if query in help_triggers or query.startswith("help"):
        return "help"
        
    return None
