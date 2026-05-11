import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from ingestion import main as run_ingestion

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scheduled_task():
    logger.info("Starting scheduled knowledge base refresh...")
    try:
        run_ingestion()
        logger.info("Scheduled refresh completed successfully.")
    except Exception as e:
        logger.error(f"Scheduled refresh failed: {e}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Schedule to run every day at 00:00 (Midnight)
    scheduler.add_job(scheduled_task, 'cron', hour=0, minute=0)
    
    # For testing: run once immediately, then every 24 hours
    # scheduler.add_job(scheduled_task, 'interval', hours=24)

    
    scheduler.start()
    logger.info("Automated Scheduler started. Knowledge base will refresh daily at 00:00.")

    try:
        # Keep the main thread alive
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()

if __name__ == "__main__":
    start_scheduler()
