import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from .batch_crawler import crawl_article_range
from .database import get_connection

class ScheduledCrawler:
    def __init__(self, config_file: str = "crawler_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load crawler configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Default configuration
        default_config = {
            "last_crawled_number": 1668,  # Start from a known article
            "last_crawl_date": None,
            "max_articles_per_month": 20,  # Safety limit
            "delay_between_requests": 1.0,
            "auto_increment_limit": 50  # How far to look for new articles
        }
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Dict = None):
        """Save crawler configuration to file"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def should_run_monthly_crawl(self) -> bool:
        """Check if monthly crawl should run"""
        if not self.config.get("last_crawl_date"):
            return True
        
        last_crawl = datetime.fromisoformat(self.config["last_crawl_date"])
        next_crawl = last_crawl + timedelta(days=30)
        
        return datetime.now() >= next_crawl
    
    async def find_new_articles(self, start_number: int, max_look_ahead: int = 50) -> List[int]:
        """Find new articles by checking which numbers exist"""
        new_articles = []
        
        for i in range(max_look_ahead):
            article_number = start_number + i + 1
            url = f"https://kjcn.or.kr/journal/view.php?number={article_number}"
            
            try:
                import httpx
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        # Check if it's a valid article page (not 404)
                        if "유효한 KJCN 저널 기사를 찾을 수 없습니다" not in response.text:
                            new_articles.append(article_number)
                            print(f"Found new article: {article_number}")
                        else:
                            print(f"Article {article_number} not found, stopping search")
                            break
                    else:
                        print(f"Article {article_number} returned status {response.status_code}")
                        break
                        
            except Exception as e:
                print(f"Error checking article {article_number}: {e}")
                break
            
            # Small delay to be respectful
            await asyncio.sleep(0.5)
        
        return new_articles
    
    async def monthly_crawl(self) -> Dict:
        """Perform monthly crawl of new articles"""
        print(f"=== MONTHLY CRAWL - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
        
        if not self.should_run_monthly_crawl():
            days_until_next = (datetime.fromisoformat(self.config["last_crawl_date"]) + 
                             timedelta(days=30) - datetime.now()).days
            return {
                "status": "skipped",
                "message": f"Monthly crawl not due yet. Next crawl in {days_until_next} days.",
                "last_crawl": self.config["last_crawl_date"]
            }
        
        # Find new articles
        last_number = self.config["last_crawled_number"]
        print(f"Searching for new articles starting from {last_number + 1}")
        
        new_articles = await self.find_new_articles(last_number, self.config["auto_increment_limit"])
        
        if not new_articles:
            print("No new articles found")
            self.config["last_crawl_date"] = datetime.now().isoformat()
            self.save_config()
            return {
                "status": "no_new_articles",
                "message": "No new articles found",
                "last_crawled_number": last_number
            }
        
        # Limit the number of articles to crawl
        max_articles = min(len(new_articles), self.config["max_articles_per_month"])
        articles_to_crawl = new_articles[:max_articles]
        
        print(f"Found {len(new_articles)} new articles, crawling {max_articles}")
        
        # Crawl the articles
        start_number = min(articles_to_crawl)
        end_number = max(articles_to_crawl)
        
        results = await crawl_article_range(
            start_number, 
            end_number, 
            self.config["delay_between_requests"]
        )
        
        # Update configuration
        successful_crawls = [r for r in results if r["status"] == "success"]
        if successful_crawls:
            self.config["last_crawled_number"] = max([r["article_number"] for r in successful_crawls])
        
        # Clean up oldest articles if new ones were added
        cleanup_result = None
        if successful_crawls:
            print(f"Cleaning up {len(successful_crawls)} oldest articles...")
            cleanup_result = await self.cleanup_oldest_articles(len(successful_crawls))
        
        self.config["last_crawl_date"] = datetime.now().isoformat()
        self.save_config()
        
        return {
            "status": "completed",
            "message": f"Monthly crawl completed. Crawled {len(successful_crawls)} articles.",
            "articles_crawled": len(successful_crawls),
            "articles_found": len(new_articles),
            "last_crawled_number": self.config["last_crawled_number"],
            "cleanup_result": cleanup_result,
            "results": results
        }
    
    async def cleanup_oldest_articles(self, count: int) -> Dict:
        """Delete the oldest articles from the database"""
        try:
            connection = get_connection()
            cursor = connection.cursor()
            
            # Get total count first
            cursor.execute("SELECT COUNT(*) FROM issues")
            total_count = cursor.fetchone()[0]
            
            if total_count <= count:
                print(f"Not enough articles to delete. Total: {total_count}, Requested: {count}")
                return {
                    "status": "skipped",
                    "message": f"Not enough articles to delete. Total: {total_count}, Requested: {count}",
                    "articles_deleted": 0
                }
            
            # Get the oldest articles (by created_at)
            cursor.execute("""
                SELECT id, title, created_at 
                FROM issues 
                ORDER BY created_at ASC 
                LIMIT %s
            """, (count,))
            
            oldest_articles = cursor.fetchall()
            
            # Delete the oldest articles
            article_ids = [article[0] for article in oldest_articles]
            placeholders = ','.join(['%s'] * len(article_ids))
            
            cursor.execute(f"DELETE FROM issues WHERE id IN ({placeholders})", article_ids)
            connection.commit()
            
            deleted_count = cursor.rowcount
            
            print(f"Deleted {deleted_count} oldest articles:")
            for article in oldest_articles:
                print(f"  - ID {article[0]}: {article[1]} (created: {article[2]})")
            
            cursor.close()
            connection.close()
            
            return {
                "status": "completed",
                "message": f"Deleted {deleted_count} oldest articles",
                "articles_deleted": deleted_count,
                "deleted_articles": [
                    {
                        "id": article[0],
                        "title": article[1],
                        "created_at": str(article[2])
                    } for article in oldest_articles
                ]
            }
            
        except Exception as e:
            print(f"Error cleaning up oldest articles: {e}")
            return {
                "status": "error",
                "message": f"Error cleaning up oldest articles: {e}",
                "articles_deleted": 0
            }

    async def manual_crawl_from(self, start_number: int, count: int = 10) -> Dict:
        """Manual crawl from a specific article number"""
        print(f"=== MANUAL CRAWL FROM {start_number} ===")
        
        end_number = start_number + count - 1
        results = await crawl_article_range(
            start_number, 
            end_number, 
            self.config["delay_between_requests"]
        )
        
        # Update last crawled number
        successful_crawls = [r for r in results if r["status"] == "success"]
        if successful_crawls:
            self.config["last_crawled_number"] = max([r["article_number"] for r in successful_crawls])
            self.save_config()
        
        return {
            "status": "completed",
            "message": f"Manual crawl completed. Crawled {len(successful_crawls)} articles.",
            "articles_crawled": len(successful_crawls),
            "results": results
        }

# Global instance
scheduled_crawler = ScheduledCrawler() 