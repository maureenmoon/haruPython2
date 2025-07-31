import asyncio
from typing import List, Dict
from .crawler import crawl_kjcn_article

async def crawl_article_range(start_number: int, end_number: int, delay: float = 1.0) -> List[Dict]:
    """
    Crawl a range of articles with incrementing numbers
    
    Args:
        start_number: Starting article number (e.g., 1669)
        end_number: Ending article number (e.g., 1675)
        delay: Delay between requests in seconds (default: 1.0)
    
    Returns:
        List of results for each article
    """
    results = []
    
    print(f"Starting batch crawl from article {start_number} to {end_number}")
    print("=" * 60)
    
    for article_number in range(start_number, end_number + 1):
        url = f"https://kjcn.or.kr/journal/view.php?number={article_number}"
        
        print(f"\nCrawling article {article_number}: {url}")
        print("-" * 50)
        
        try:
            result = await crawl_kjcn_article(url)
            
            if "error" in result:
                print(f"❌ Article {article_number}: {result['error']}")
                results.append({
                    "article_number": article_number,
                    "url": url,
                    "status": "error",
                    "error": result["error"]
                })
            else:
                print(f"✅ Article {article_number}: {result['title']}")
                results.append({
                    "article_number": article_number,
                    "url": url,
                    "status": "success",
                    "title": result["title"],
                    "content_length": len(result["content"]),
                    "reference": result["reference"]
                })
                
        except Exception as e:
            print(f"❌ Article {article_number}: Exception - {e}")
            results.append({
                "article_number": article_number,
                "url": url,
                "status": "exception",
                "error": str(e)
            })
        
        # Add delay between requests to be respectful to the server
        if article_number < end_number:
            print(f"Waiting {delay} seconds before next request...")
            await asyncio.sleep(delay)
    
    # Print summary
    print("\n" + "=" * 60)
    print("BATCH CRAWL SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r["status"] == "success")
    errors = sum(1 for r in results if r["status"] == "error")
    exceptions = sum(1 for r in results if r["status"] == "exception")
    
    print(f"Total articles: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Errors: {errors}")
    print(f"Exceptions: {exceptions}")
    
    return results

async def crawl_next_articles(current_number: int, count: int = 5, delay: float = 1.0) -> List[Dict]:
    """
    Crawl the next N articles starting from current number
    
    Args:
        current_number: Current article number (e.g., 1669)
        count: Number of articles to crawl (default: 5)
        delay: Delay between requests in seconds (default: 1.0)
    
    Returns:
        List of results for each article
    """
    start_number = current_number + 1
    end_number = current_number + count
    
    return await crawl_article_range(start_number, end_number, delay)

async def crawl_previous_articles(current_number: int, count: int = 5, delay: float = 1.0) -> List[Dict]:
    """
    Crawl the previous N articles starting from current number
    
    Args:
        current_number: Current article number (e.g., 1669)
        count: Number of articles to crawl (default: 5)
        delay: Delay between requests in seconds (default: 1.0)
    
    Returns:
        List of results for each article
    """
    start_number = current_number - count
    end_number = current_number - 1
    
    return await crawl_article_range(start_number, end_number, delay) 