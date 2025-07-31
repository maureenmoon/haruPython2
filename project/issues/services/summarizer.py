from ..utils.chunk_utils import chunk_text
from ..utils.openai_utils import summarize_text

def summarize_article_content(full_text: str) -> str:
    """
    Summarize article content by chunking and processing each chunk
    """
    print("STEP 3: Starting summarization")
    
    chunks = chunk_text(full_text)
    summaries = [summarize_text(chunk) for chunk in chunks]
    full_summary = "\n".join(summaries)
    
    print("STEP 4: Finished summarization")
    return full_summary

