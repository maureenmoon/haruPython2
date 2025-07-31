import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from issues.services.crawler import crawl_kjcn_article

async def test_multiple_articles():
    # Test URLs - different KJCN journal article numbers
    test_urls = [
        "https://kjcn.or.kr/journal/view.php?number=1671",  # Current test article
        "https://kjcn.or.kr/journal/view.php?number=1672",  # Try a different article
        "https://kjcn.or.kr/journal/view.php?number=1673",  # Try another article
        "https://kjcn.or.kr/journal/view.php?number=1674",  # Try another article
        "https://kjcn.or.kr/journal/view.php?number=1675",  # Current test article
        "https://kjcn.or.kr/journal/view.php?number=1676",  # Try a different article
        "https://kjcn.or.kr/journal/view.php?number=1677",  # Try another article
        "https://kjcn.or.kr/journal/view.php?number=1678",  # Try another article
        "https://kjcn.or.kr/journal/view.php?number=1679",  # Try another article
        "https://kjcn.or.kr/journal/view.php?number=1680",  # Try another article
    ]
    
    print("=== TESTING KJCN JOURNAL ARTICLE TITLE EXTRACTION ===")
    print()
    
    for i, url in enumerate(test_urls, 1):
        print(f"KJCN Article {i}: {url}")
        print("-" * 80)
        
        try:
            result = await crawl_kjcn_article(url)
            
            if "error" in result:
                print(f"ERROR: {result['error']}")
            else:
                print(f"Title: {result['title']}")
                print(f"Content length: {len(result['content'])} characters")
                print(f"Reference: {result['reference']}")
            
            print()
            
        except Exception as e:
            print(f"EXCEPTION: {e}")
            print()
        
        # Add a small delay between requests
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_multiple_articles()) 