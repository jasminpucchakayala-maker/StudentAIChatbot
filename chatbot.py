import json
import time
import random
import os
import config
from utils.matcher import find_best_intent, detect_conversational_intent
from utils.history import save_chat_record

class StudentChatbot:
    def __init__(self):
        self.intents = []
        self.load_intents()
        
    def load_intents(self):
        """Load knowledge base categories from the intents.json file."""
        if os.path.exists(config.INTENTS_FILE):
            try:
                with open(config.INTENTS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.intents = data.get("intents", [])
            except Exception as e:
                print(f"Error loading intents JSON: {e}")
                self.intents = []
        else:
            print(f"Warning: intents.json file not found at {config.INTENTS_FILE}")
            self.intents = []

    def get_response(self, user_query: str, session_id: str = "default_session") -> dict:
        """
        Processes human questions, runs matching, chooses response, logs metrics, 
        and records transaction into the local history database.
        """
        start_time = time.perf_counter()
        
        # 1. Edge query validations
        if not user_query.strip():
            execution_time = time.perf_counter() - start_time
            return {
                "response": "Please type a question and I will help you find answers!",
                "intent": "empty_query",
                "confidence": 1.0,
                "suggestions": config.SUGGESTED_QUESTIONS[:4],
                "response_time": execution_time
            }
            
        # 2. Check for conversation filler terms (Greetings, parting, bio details)
        convo_tag = detect_conversational_intent(user_query)
        
        if convo_tag:
            res_text = ""
            suggestions = config.SUGGESTED_QUESTIONS[:4]
            
            if convo_tag == "greeting":
                res_text = random.choice(config.RANDOM_GREETINGS)
            elif convo_tag == "goodbye":
                res_text = random.choice(config.RANDOM_FAREWELLS)
                suggestions = []
            elif convo_tag == "thanks":
                res_text = random.choice(config.RANDOM_THANKS)
            elif convo_tag == "identity":
                res_text = (
                    f"I am **{config.APP_TITLE}** ({config.APP_VERSION}), a virtual AI academic copilot. "
                    f"I was created to assist students with quick inquiries regarding college admissions, fees, "
                    f"hostels, course eligibility, clubs, exams, and canteen options. Ask me anything!"
                )
            elif convo_tag == "help":
                res_text = (
                    "I can answer academic queries across various categories! Here are some things you can ask:\n"
                    "- **Admissions & Courses**: 'How to take admission?' or 'Tell me about computer science.'\n"
                    "- **Fines, Fees & Scholarships**: 'Show me the tuition fees' or 'Are scholarships available?'\n"
                    "- **Infrastructure & Operations**: 'Is there a college hostel?' or 'What are the office timings?'\n"
                    "- **Rules & Safety**: 'What is your minimum academic attendance?' or 'Is there an anti-ragging cell?'\n\n"
                    "Use the FAQ cards and suggestion chips to explore quickly!"
                )
            
            execution_time = time.perf_counter() - start_time
            
            # Log conversational events to history too
            save_chat_record(
                session_id=session_id,
                question=user_query,
                response=res_text,
                intent=convo_tag,
                confidence=1.0,
                response_time=execution_time
            )
            
            return {
                "response": res_text,
                "intent": convo_tag,
                "confidence": 1.0,
                "suggestions": suggestions,
                "response_time": execution_time
            }
            
        # 3. Apply hybrid similarity NLP scanner on knowledge base
        match_result = find_best_intent(user_query, self.intents)
        intent_tag = match_result["tag"]
        confidence = match_result["confidence"]
        matched_responses = match_result["responses"]
        matched_suggestions = match_result["suggestions"]
        
        # Determine Response
        if confidence >= config.MATCH_THRESHOLD:
            # High confidence selection
            response_text = random.choice(matched_responses)
        elif confidence >= config.SUGGESTION_THRESHOLD:
            # Medium confidence - warn user but provide answers
            topic = intent_tag.replace("_", " ").capitalize()
            raw_response = random.choice(matched_responses)
            response_text = (
                f"⚠️ *I found a partial match related to **{topic}** (Confidence: {int(confidence*100)}%).*\n\n"
                f"{raw_response}\n\n"
                f"*If this was not what you were looking for, look at the suggestions below or rephrase.*"
            )
            if not matched_suggestions:
                matched_suggestions = config.SUGGESTED_QUESTIONS[:3]
        else:
            # Fallback
            response_text = random.choice(config.FALLBACK_RESPONSES)
            intent_tag = "unknown"
            # Return top queries as suggestions during fallbacks
            matched_suggestions = config.SUGGESTED_QUESTIONS[:4]
            
        execution_time = time.perf_counter() - start_time
        
        # 4. Save to CSV log database
        save_chat_record(
            session_id=session_id,
            question=user_query,
            response=response_text,
            intent=intent_tag,
            confidence=confidence,
            response_time=execution_time
        )
        
        return {
            "response": response_text,
            "intent": intent_tag,
            "confidence": confidence,
            "suggestions": matched_suggestions,
            "response_time": execution_time
        }
