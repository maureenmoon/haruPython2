import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from issues.services.scheduled_crawler import scheduled_crawler

async def test_monthly_crawler():
    print("=== Testing Monthly Crawler Functionality ===")
    print()
    
    # Test 1: Check crawler status
    print("1. Current Crawler Status:")
    print("-" * 40)
    config = scheduled_crawler.config
    print(f"Last crawled number: {config['last_crawled_number']}")
    print(f"Last crawl date: {config['last_crawl_date']}")
    print(f"Max articles per month: {config['max_articles_per_month']}")
    print(f"Auto increment limit: {config['auto_increment_limit']}")
    print()
    
    # Test 2: Check if monthly crawl should run
    print("2. Should Run Monthly Crawl:")
    print("-" * 40)
    should_run = scheduled_crawler.should_run_monthly_crawl()
    print(f"Should run: {should_run}")
    if not should_run and config.get("last_crawl_date"):
        from datetime import datetime, timedelta
        last_crawl = datetime.fromisoformat(config["last_crawl_date"])
        next_crawl = last_crawl + timedelta(days=30)
        days_until = (next_crawl - datetime.now()).days
        print(f"Days until next crawl: {days_until}")
    print()
    
    # Test 3: Find new articles
    print("3. Finding New Articles:")
    print("-" * 40)
    last_number = config["last_crawled_number"]
    new_articles = await scheduled_crawler.find_new_articles(last_number, 30)
    print(f"Found {len(new_articles)} new articles: {new_articles}")
    print()
    
    # Test 4: Manual crawl (small test)
    print("4. Manual Crawl Test (2 articles):")
    print("-" * 40)
    if new_articles:
        start_number = new_articles[0]
        result = await scheduled_crawler.manual_crawl_from(start_number, 2)
        print(f"Result: {result['message']}")
        print(f"Articles crawled: {result['articles_crawled']}")
    else:
        print("No new articles to crawl")
    print()
    
    # Test 5: Monthly crawl (if due)
    print("5. Monthly Crawl Test:")
    print("-" * 40)
    if should_run:
        result = await scheduled_crawler.monthly_crawl()
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        if result['status'] == 'completed':
            print(f"Articles crawled: {result['articles_crawled']}")
            if 'cleanup_result' in result and result['cleanup_result']:
                cleanup = result['cleanup_result']
                print(f"Cleanup: {cleanup['message']}")
    else:
        print("Monthly crawl not due yet")
    
    # Test 6: Manual cleanup test
    print("\n6. Manual Cleanup Test:")
    print("-" * 40)
    cleanup_result = await scheduled_crawler.cleanup_oldest_articles(2)
    print(f"Cleanup status: {cleanup_result['status']}")
    print(f"Cleanup message: {cleanup_result['message']}")
    if cleanup_result['status'] == 'completed':
        print(f"Articles deleted: {cleanup_result['articles_deleted']}")
        for article in cleanup_result.get('deleted_articles', []):
            print(f"  - Deleted: {article['title']} (ID: {article['id']})")

if __name__ == "__main__":
    asyncio.run(test_monthly_crawler()) 