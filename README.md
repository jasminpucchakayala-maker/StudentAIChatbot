# CHINGU AI - Professional Student Query Chatbot Platform

CHINGU AI is an internship-level, high-fidelity AI-based Student Query Chatbot. It provides students with instant, accurate, and context-aware responses to standard academic and campus life questions while logging system metrics and providing a live Plotly analytics dashboard for institutional administrators.

---

## Key Features

### 🤖 Smart Chat Bot
* **Advanced NLP Pipeline**: Tokenization, Stopword removal, and WordNet Lemmatization using NLTK.
* **Hybrid Matching Algorithm**: Combines string similarity (sequence ratios via SequenceMatcher) with set-theory token similarities (Jaccard and Overlap Coefficients) to build robust confidence maps.
* **Conversational Filter Triggers**: Custom match handling for greetings, farewells, gratitude, identity parameters, and help menus.
* **Suggested Queries**: Live suggested follow-up questions render dynamically based on the bot's confidence triggers.
* **Theme Switching**: Custom light mode and dark mode styles matching a medical/cyber-tech turquoise theme.

### 📊 System Diagnostics Dashboard
* **Dynamic KPI Indicators**: Track total conversations, questions asked today, median model confidence, and average system response speed.
* **Visual Analytics Plots**: Beautifully styled Plotly charts showing:
  - Frequency distribution of topic categories.
  - Recognition accuracy categorizations (High, Medium, Lossy counts).
  - Time-series performance trend lines of average response speeds.
* **Interactive Log Table**: Search and filter through raw transaction records.
* **Data Log Exporter**: Instantly download logs as standard CSV records or full JSON session transcripts.

---

## Directory Structure

```text
StudentAIChatbot/
├── app.py                     # Main Streamlit web application entrypoint
├── chatbot.py                 # Chatbot core logic class (coordinates NLP + matching + replies)
├── config.py                  # Colors, settings, directories, default suggestions
├── requirements.txt           # Dependency specifications
├── README.md                  # Professional documentation for the project
├── intents.json               # Knowledge base containing 22 categories, 11-12 patterns each
├── chatbot_history.csv        # Auto-saved conversation logs (created programmatically)
├── assets/                    # Image assets (Logo, Bot avatar, backgrounds)
│   ├── logo.png
│   ├── chatbot.png
│   └── background.jpg
├── styles/
│   └── style.css              # Custom styling for professional glassmorphism, chatbot UI, cards
└── utils/
    ├── text_processing.py     # NLTK integration: Tokenization, lemmatization, stopword cleaning
    ├── matcher.py             # Pattern and keyword similarity matching engine (difflib/fuzzy-matching)
    ├── history.py             # Functions to load, save, download, and export conversation history
    └── helpers.py             # Timing, quick-suggestions, theme utilities, metric processing
```

---

## Installation & Setup

Ensure Python 3.8+ is installed on your local environment.

### 1. Clone or Move to the Directory
Navigate to the root project folder:
```bash
cd StudentAIChatbot
```

### 2. Install Dependencies
Install all required models and tools listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```
*Note: On launch, the application will automatically check for and download necessary NLTK packages (`punkt`, `stopwords`, `wordnet`) silently without any user action.*

### 3. Run the Streamlit Application
Execute the Streamlit server:
```bash
streamlit run app.py
```

---

## System Architecture & NLP Workflow

1. **Input Cleanse**: Converts comments to lowercase, strips punctuation, and normalizes space characters.
2. **NLTK Processing**:
   - Tokenizes strings into isolated lexemes.
   - Cleans connector words via localized Stopwords corpus.
   - Normalizes verbs and plurals using `WordNetLemmatizer` (e.g. `exams` or `examining` $\to$ `exam`).
3. **Double-Ended Match Indexing**:
   - Compares the character-level similarity ratios using `SequenceMatcher` / `difflib`.
   - Computes intersection metrics (Jaccard index and Overlap coefficient) to determine keyword overlap.
   - Evaluates a weighted hybrid confidence score.
4. **Conditional Trigger Resolution**:
   - **Confidence >= 55%**: Selects response randomly from matched category.
   - **Confidence between 35% and 55%**: Replies with the matches, warning the user about partial confidence levels, and displays matched suggested prompts.
   - **Confidence < 35%**: Returns a random fallback response suggesting general categories.
5. **Autosave Transaction Logs**: Logs execution data to `chatbot_history.csv` including timestamp, session ID, user question, response text, classification, confidence, and speed.

---

## Future Enhancements
* **Vectorizer Integration**: Upgrade fuzzy token matching with custom TF-IDF or Word2Vec embeddings for semantic understanding.
* **Voice Support**: Support text-to-speech feedback and speech-to-text queries.
* **ERP Database Integration**: Connect to real-time university database servers to show individual GPA/attendance stats dynamically on credential verification.

---

## Author & License
* **Developer**: Antigravity Dev Team & Student Intern
* **License**: MIT License
