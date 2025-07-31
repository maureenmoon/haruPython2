import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def translate_to_korean(text: str) -> str:
    """
    Translate English text to Korean using OpenAI API
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator. Translate the given English text to Korean. Maintain the academic and formal tone appropriate for journal articles. Return only the Korean translation without any additional text or explanations."
                },
                {
                    "role": "user",
                    "content": f"Translate this English text to Korean: {text}"
                }
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        korean_translation = response.choices[0].message.content.strip()
        print(f"Translation: '{text}' -> '{korean_translation}'")
        return korean_translation
        
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails

def is_english_text(text: str) -> bool:
    """
    Check if text is primarily English (contains mostly English characters)
    """
    if not text:
        return False
    
    # Count English characters vs Korean characters
    english_chars = sum(1 for char in text if char.isascii() and char.isalpha())
    korean_chars = sum(1 for char in text if '\u3131' <= char <= '\u318E' or '\uAC00' <= char <= '\uD7A3')
    
    # If more English characters than Korean, consider it English
    return english_chars > korean_chars

def get_korean_title(title: str) -> str:
    """
    Get Korean title - either use existing Korean title or translate English to Korean
    """
    if not title or title == "제목 없음":
        return title
    
    # If it's already Korean, return as is
    if not is_english_text(title):
        return title
    
    # If it's English, translate to Korean
    print(f"Translating English title to Korean: {title}")
    return translate_to_korean(title)

def summarize_title(title: str, max_words: int = 5) -> str:
    """
    Create a short, concise title (max 5 words) using OpenAI
    """
    try:
        # Check if title is Korean or English for better prompting
        is_english = is_english_text(title)
        
        if is_english:
            system_prompt = f"You are a title summarizer. Create a very short, concise title with maximum {max_words} words that captures the main topic of the given title. Focus on the key subject and main concept. Return only the summarized title without quotes or additional text."
        else:
            system_prompt = f"You are a Korean title summarizer. Create a very short, concise Korean title with maximum {max_words} words that captures the main topic of the given Korean title. Focus on the key subject and main concept. Return only the summarized Korean title without quotes or additional text."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Summarize this title to maximum {max_words} words: {title}"
                }
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        summarized_title = response.choices[0].message.content.strip()
        print(f"Title summarization: '{title}' -> '{summarized_title}'")
        return summarized_title
        
    except Exception as e:
        print(f"Title summarization error: {e}")
        # Fallback: return first few words
        if is_english_text(title):
            words = title.split()[:max_words]
            return " ".join(words)
        else:
            # For Korean, try to get first few characters
            return title[:20] if len(title) > 20 else title

def get_short_korean_title(title: str, max_words: int = 5) -> str:
    """
    Get a short Korean title - translate if needed and then summarize
    """
    if not title or title == "제목 없음":
        return title
    
    # Check if it's English or Korean
    is_english = is_english_text(title)
    
    if is_english:
        # If English, translate to Korean first, then summarize
        print(f"Translating English title to Korean: {title}")
        korean_title = translate_to_korean(title)
        print(f"Translated to Korean: {korean_title}")
        
        # Summarize the Korean title
        short_title = summarize_title(korean_title, max_words)
        print(f"Summarized Korean title: {short_title}")
        
    else:
        # If already Korean, just summarize
        print(f"Title is already Korean: {title}")
        short_title = summarize_title(title, max_words)
        print(f"Summarized Korean title: {short_title}")
    
    return short_title 