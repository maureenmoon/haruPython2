from fastapi import APIRouter, Depends, Header, HTTPException
from .services.crawler import crawl_kjcn_article
from .services.batch_crawler import crawl_article_range, crawl_next_articles, crawl_previous_articles
from .services.scheduled_crawler import scheduled_crawler
from .crud_routes import router as crud_router, verify_admin_role

router = APIRouter()

# # Test endpoint to check if scheduled_crawler import works
# @router.get("/test-scheduled-crawler")
# async def test_scheduled_crawler():
#     """Test if scheduled_crawler import is working"""
#     try:
#         print("[DEBUG] Testing scheduled_crawler import...")
#         config = scheduled_crawler.config
#         print("[DEBUG] scheduled_crawler.config:", config)
#         return {"status": "success", "config": config}
#     except Exception as e:
#         print("[DEBUG] Error with scheduled_crawler:", e)
#         return {"status": "error", "error": str(e)}

# @router.get("/crawler-status-test")
# async def crawler_status_test():
#     """
#     Test crawler status without admin verification
#     """
#     print("[DEBUG] ===== CRAWLER_STATUS_TEST FUNCTION CALLED =====")
    
#     try:
#         print("[DEBUG] About to access scheduled_crawler.config")
#         config = scheduled_crawler.config
#         print("[DEBUG] Successfully got config:", config)
        
#         days_until_next = None
#         if config.get("last_crawl_date"):
#             from datetime import datetime, timedelta
#             last_crawl = datetime.fromisoformat(config["last_crawl_date"])
#             next_crawl = last_crawl + timedelta(days=30)
#             days_until_next = (next_crawl - datetime.now()).days
        
#         result = {
#             "last_crawled_number": config["last_crawled_number"],
#             "last_crawl_date": config["last_crawl_date"],
#             "days_until_next_crawl": days_until_next,
#             "max_articles_per_month": config["max_articles_per_month"],
#             "auto_increment_limit": config["auto_increment_limit"]
#         }
        
#         print("[DEBUG] crawler_status_test returning:", result)
#         return result
        
#     except Exception as e:
#         print("[DEBUG] Error in crawler_status_test:", e)
#         raise HTTPException(status_code=500, detail=f"Test error: {str(e)}")


@router.get("/crawl")
async def crawl(url: str, admin_verified: bool = Depends(verify_admin_role)):
    print("STEP 1: received url to crawl:", url)
    result = await crawl_kjcn_article(url)
    print("STEP 2: Finished crawl_kjcn_article, returning result")
    return result

@router.get("/crawl-range")
async def crawl_range(start_number: int, end_number: int, delay: float = 1.0, admin_verified: bool = Depends(verify_admin_role)):
    """
    Crawl a range of articles with incrementing numbers
    Example: /issues/crawl-range?start_number=1669&end_number=1675
    """
    results = await crawl_article_range(start_number, end_number, delay)
    return {
        "message": f"Batch crawl completed for articles {start_number} to {end_number}",
        "results": results
    }

@router.get("/crawl-next")
async def crawl_next(current_number: int, count: int = 5, delay: float = 1.0, admin_verified: bool = Depends(verify_admin_role)):
    """
    Crawl the next N articles starting from current number
    Example: /issues/crawl-next?current_number=1669&count=3
    """
    results = await crawl_next_articles(current_number, count, delay)
    return {
        "message": f"Crawled next {count} articles starting from {current_number}",
        "results": results
    }

@router.get("/crawl-previous")
async def crawl_previous(current_number: int, count: int = 5, delay: float = 1.0, admin_verified: bool = Depends(verify_admin_role)):
    """
    Crawl the previous N articles starting from current number
    Example: /issues/crawl-previous?current_number=1669&count=3
    """
    results = await crawl_previous_articles(current_number, count, delay)
    return {
        "message": f"Crawled previous {count} articles ending at {current_number}",
        "results": results
    }

@router.get("/monthly-crawl")
async def monthly_crawl(admin_verified: bool = Depends(verify_admin_role)):
    """
    Run monthly crawl to find and crawl new articles
    Automatically checks if it's time to run (every 30 days)
    """
    result = await scheduled_crawler.monthly_crawl()
    return result

@router.get("/manual-crawl")
async def manual_crawl(start_number: int, count: int = 10, admin_verified: bool = Depends(verify_admin_role)):
    """
    Manual crawl from a specific article number
    Example: /issues/manual-crawl?start_number=1670&count=5
    """
    result = await scheduled_crawler.manual_crawl_from(start_number, count)
    return result

@router.get("/crawler-status")
async def crawler_status(admin_verified: bool = Depends(verify_admin_role)):
    """
    Get current crawler configuration and status
    """
    print("[DEBUG] crawler_status function called")
    print("[DEBUG] Function entry point reached")

    try:
        print("[DEBUG] About to access scheduled_crawler.config")
        config = scheduled_crawler.config
        print("[DEBUG] Successfully got config:", config)
    except Exception as e:
        print("[DEBUG] Error accessing scheduled_crawler.config:", e)
        raise HTTPException(status_code=500, detail=f"Config error: {str(e)}")
    
    print("[DEBUG] admin_verified:", admin_verified)
    
    config = scheduled_crawler.config
    print("[DEBUG] scheduled_crawler.config:", config)
    
    days_until_next = None
    
    if config.get("last_crawl_date"):
        from datetime import datetime, timedelta
        last_crawl = datetime.fromisoformat(config["last_crawl_date"])
        next_crawl = last_crawl + timedelta(days=30)
        days_until_next = (next_crawl - datetime.now()).days
    
    result = {
        "last_crawled_number": config["last_crawled_number"],
        "last_crawl_date": config["last_crawl_date"],
        "days_until_next_crawl": days_until_next,
        "max_articles_per_month": config["max_articles_per_month"],
        "auto_increment_limit": config["auto_increment_limit"]
    }
    
    print("[DEBUG] crawler_status returning:", result)
    return result

@router.get("/crawler-status-test")
async def crawler_status_test():
    """
    Test crawler status without admin verification
    """
    print("[DEBUG] ===== CRAWLER_STATUS_TEST FUNCTION CALLED =====")
    
    try:
        print("[DEBUG] About to access scheduled_crawler.config")
        config = scheduled_crawler.config
        print("[DEBUG] Successfully got config:", config)
        
        days_until_next = None
        if config.get("last_crawl_date"):
            from datetime import datetime, timedelta
            last_crawl = datetime.fromisoformat(config["last_crawl_date"])
            next_crawl = last_crawl + timedelta(days=30)
            days_until_next = (next_crawl - datetime.now()).days
        
        result = {
            "last_crawled_number": config["last_crawled_number"],
            "last_crawl_date": config["last_crawl_date"],
            "days_until_next_crawl": days_until_next,
            "max_articles_per_month": config["max_articles_per_month"],
            "auto_increment_limit": config["auto_increment_limit"]
        }
        
        print("[DEBUG] crawler_status_test returning:", result)
        return result
        
    except Exception as e:
        print("[DEBUG] Error in crawler_status_test:", e)
        raise HTTPException(status_code=500, detail=f"Test error: {str(e)}")

    
@router.get("/cleanup-oldest")
async def cleanup_oldest(count: int = 10, admin_verified: bool = Depends(verify_admin_role)):
    """
    Manually delete the oldest N articles from the database
    Example: /issues/cleanup-oldest?count=5
    """
    result = await scheduled_crawler.cleanup_oldest_articles(count)
    return result

# Include CRUD routes
router.include_router(crud_router, tags=["issues-crud"])

# Root endpoint moved to CRUD routes to avoid conflict
# @router.get("/")
# def issues_root():
#     return {"status": "Issues API is running"} 