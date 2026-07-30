import re
import string
import nltk

def _init_nltk():
    """Download required NLTK resources if not already present."""
    resources = {
        'tokenizers/punkt': 'punkt',
        'corpora/stopwords': 'stopwords',
        'corpora/wordnet': 'wordnet',
        'corpora/omw-1.4': 'omw-1.4',
        'tokenizers/punkt_tab': 'punkt_tab',
    }
    for path, package in resources.items():
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                nltk.download(package, quiet=True)
            except Exception as e:
                print(f"Warning: Failed to download NLTK package {package}: {e}")

# Run NLTK download initialization
_init_nltk()

try:
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    STOP_WORDS = set(stopwords.words('english'))
    LEMMATIZER = WordNetLemmatizer()
except Exception as e:
    # Fail-safe indicators in case NLTK suffers connectivity issues on compilation
    print(f"Warning: Falling back to primitive tokenization. NLTK loading failed: {e}")
    STOP_WORDS = {"the", "a", "an", "is", "are", "to", "for", "in", "of", "and", "or", "what", "how", "where", "why", "who", "which"}
    class DummyLemmatizer:
        def lemmatize(self, token):
            return token.lower().strip()
    LEMMATIZER = DummyLemmatizer()
    def word_tokenize(text):
        return text.split()

def clean_text(text: str) -> str:
    """Lowercase, strip spacing, and remove punctuation/special signs."""
    if not text:
        return ""
    # Lowercase
    text = text.lower().strip()
    # Remove punctuation
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)
    return text

def preprocess_text(text: str) -> list:
    """Preprocess text by cleaning, tokenizing, removing stopwords, and lemmatizing."""
    cleaned = clean_text(text)
    if not cleaned:
        return []
    
    # Tokenize
    tokens = word_tokenize(cleaned)
    
    # Remove stopwords and lemmatize
    cleaned_tokens = [
        LEMMATIZER.lemmatize(token) 
        for token in tokens 
        if token not in STOP_WORDS
    ]
    
    return cleaned_tokens

def extract_keywords(text: str) -> set:
    """Extract unique lemmatized keywords from the sentence."""
    processed = preprocess_text(text)
    return set(processed)
