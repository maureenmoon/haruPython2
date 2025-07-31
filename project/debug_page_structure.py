import httpx
from bs4 import BeautifulSoup
import asyncio

async def debug_page_structure():
    url = "https://kjcn.or.kr/journal/view.php?number=1671"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        print("=== DEBUGGING PAGE STRUCTURE ===")
        print(f"URL: {url}")
        print()
        
        # Look for elements with 'tit_ko' and 'tit' classes
        print("=== SEARCHING FOR TITLE ELEMENTS ===")
        
        # Search for tit_ko (Korean title)
        tit_ko_elements = soup.find_all(class_="tit_ko")
        print(f"Found {len(tit_ko_elements)} elements with class 'tit_ko':")
        for i, elem in enumerate(tit_ko_elements):
            print(f"  {i+1}. Text: '{elem.get_text(strip=True)}'")
            print(f"     HTML: {elem}")
            print()
        
        # Search for tit (English title)
        tit_elements = soup.find_all(class_="tit")
        print(f"Found {len(tit_elements)} elements with class 'tit':")
        for i, elem in enumerate(tit_elements):
            print(f"  {i+1}. Text: '{elem.get_text(strip=True)}'")
            print(f"     HTML: {elem}")
            print()
        
        # Also search for any element containing 'tit_ko' or 'tit' in class
        print("=== SEARCHING FOR ELEMENTS CONTAINING 'tit' IN CLASS ===")
        tit_containing = soup.find_all(class_=lambda x: x and ('tit' in x))
        print(f"Found {len(tit_containing)} elements with 'tit' in class:")
        for i, elem in enumerate(tit_containing):
            classes = elem.get('class', [])
            print(f"  {i+1}. Classes: {classes}")
            print(f"     Text: '{elem.get_text(strip=True)}'")
            print(f"     Tag: {elem.name}")
            print()
        
        # Look for common title patterns
        print("=== SEARCHING FOR COMMON TITLE PATTERNS ===")
        title_patterns = [
            "h1", "h2", "h3",
            ".title", ".article-title", ".headline",
            "[class*='title']", "[class*='tit']"
        ]
        
        for pattern in title_patterns:
            elements = soup.select(pattern)
            if elements:
                print(f"Pattern '{pattern}' found {len(elements)} elements:")
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    print(f"  {i+1}. Text: '{elem.get_text(strip=True)}'")
                    print(f"     Classes: {elem.get('class', [])}")
                print()

if __name__ == "__main__":
    asyncio.run(debug_page_structure()) 