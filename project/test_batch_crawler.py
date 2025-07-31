import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from issues.services.batch_crawler import crawl_article_range, crawl_next_articles, crawl_previous_articles

async def test_batch_crawler():
    print("=== Testing Batch Crawler Functionality ===")
    print()
    
    # Test 1: Crawl next 3 articles from 1669
    print("1. Testing crawl_next_articles (1669 + 1 to 1669 + 3)")
    print("-" * 60)
    results1 = await crawl_next_articles(current_number=1669, count=3, delay=0.5)
    print()
    
    # Test 2: Crawl previous 2 articles from 1669
    print("2. Testing crawl_previous_articles (1669 - 2 to 1669 - 1)")
    print("-" * 60)
    results2 = await crawl_previous_articles(current_number=1669, count=2, delay=0.5)
    print()
    
    # Test 3: Crawl specific range
    print("3. Testing crawl_article_range (1670 to 1672)")
    print("-" * 60)
    results3 = await crawl_article_range(start_number=1670, end_number=1672, delay=0.5)
    print()
    
    # Summary
    print("=== FINAL SUMMARY ===")
    print(f"Test 1 (next 3): {len([r for r in results1 if r['status'] == 'success'])} successful")
    print(f"Test 2 (previous 2): {len([r for r in results2 if r['status'] == 'success'])} successful")
    print(f"Test 3 (range 1670-1672): {len([r for r in results3 if r['status'] == 'success'])} successful")

if __name__ == "__main__":
    asyncio.run(test_batch_crawler()) 