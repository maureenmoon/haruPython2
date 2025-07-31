import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from pathlib import Path

from .database import save_content_to_db
from .summarizer import summarize_article_content
from ..utils.translation_utils import get_short_korean_title

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

async def crawl_kjcn_article(url: str) -> dict:
    print("STEP 2: Inside crawl_kjcn_article")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title specifically for KJCN journal articles
        title = "제목 없음"
        
        # KJCN-specific title selectors (based on the site structure)
        kjcn_title_selectors = [
            ".tit_ko",  # Korean title (highest priority)
            ".tit",     # English title
        ]
        
        for selector in kjcn_title_selectors:
            title_tag = soup.select_one(selector)
            if title_tag:
                potential_title = title_tag.get_text(strip=True)
                if len(potential_title) > 5:  # Ensure it's not empty
                    title = potential_title
                    print(f"Found KJCN title using selector '{selector}': {title}")
                    break
        
        # If no title found, this might not be a valid KJCN article
        if title == "제목 없음":
            print("WARNING: No valid title found. This might not be a KJCN journal article.")
            # Return error for invalid articles
            return {"error": "유효한 KJCN 저널 기사를 찾을 수 없습니다.", "reference": url}

        # Ensure we have a short Korean title (translate and summarize if needed)
        short_korean_title = get_short_korean_title(title, max_words=5)
        print(f"Final short Korean title: {short_korean_title}")

        # Extract body sections
        article_container = soup.select_one("div.contents div.articleCon")
        if not article_container:
            return {"error": "본문을 찾을 수 없습니다.", "reference": url}

        sections = []
        for header in article_container.select("h4.link-target"):
            section_title = header.get_text(strip=True)
            next_dd = header.find_next_sibling("dd")
            if next_dd:
                section_text = next_dd.get_text(strip=True)
                sections.append(f"[{section_title}]\n{section_text}")

        full_text = "\n\n".join(sections)

        if not full_text:
            return {"error": "본문 내용이 비어 있습니다.", "reference": url}

        # Summarize the content
        full_summary = summarize_article_content(full_text)

        # Save to database - url becomes reference in DB
        save_content_to_db(short_korean_title, full_summary, url, "ADMIN")

        return {
            "title": short_korean_title,
            "content": full_summary,
            "reference": url
        }
