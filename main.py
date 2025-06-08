import sys
import os

print("=== YouTube Data Migration Tool ===")
print("Starting application...")

# Test imports first
try:
    print("Importing selenium...")
    from selenium import webdriver
    print("✓ Selenium imported")
except ImportError as e:
    print(f"✗ Failed to import selenium: {e}")
    print("Please install: pip install selenium")
    sys.exit(1)

try:
    print("Importing undetected chromedriver...")
    import undetected_chromedriver as uc
    print("✓ Undetected chromedriver imported")
except ImportError as e:
    print(f"✗ Failed to import undetected_chromedriver: {e}")
    print("Please install: pip install undetected-chromedriver")
    sys.exit(1)

try:
    print("Importing scraper module...")
    from scraper import scrape_youtube_data
    print("✓ Scraper module imported")
except ImportError as e:
    print(f"✗ Failed to import scraper: {e}")
    print("Make sure scraper.py is in the same directory")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error in scraper.py: {e}")
    sys.exit(1)

try:
    print("Importing migrator module...")
    from migratortest import migrate_youtube_data
    print("✓ Migrator module imported")
except ImportError as e:
    print(f"✗ Failed to import migrator: {e}")
    print("Make sure migrator.py is in the same directory")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error in migrator.py: {e}")
    sys.exit(1)

def get_driver():
    print("\n=== Setting up Chrome Driver ===")
    try:
        options = uc.ChromeOptions()
        
        # Add some common options to prevent issues
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        print("Creating Chrome driver...")
        driver = uc.Chrome(options=options)
        print("✓ Chrome driver created successfully!")
        
        # Test the driver
        print("Testing driver...")
        driver.get("https://www.google.com")
        print("✓ Driver test successful!")
        
        return driver
        
    except Exception as e:
        print(f"✗ Failed to create Chrome driver: {e}")
        print("\nPossible solutions:")
        print("1. Make sure Google Chrome is installed")
        print("2. Try: pip install --upgrade undetected-chromedriver")
        print("3. Check if Chrome is running in the background and close it")
        return None

def main():
    print("\n=== Starting Main Process ===")
    
    # Create driver
    driver = get_driver()
    if not driver:
        print("Cannot proceed without a working driver. Exiting.")
        return False
    
    try:
        # Navigate to YouTube to start
        print("\nNavigating to YouTube...")
        driver.get("https://www.youtube.com")
        
        print("\n" + "="*50)
        print("STEP 1: LOGIN TO YOUR CURRENT YOUTUBE ACCOUNT")
        print("="*50)
        print("Please login to your current YouTube account in the browser.")
        print("Make sure you're fully logged in before proceeding.")
        input("Press Enter when you're logged in and ready to scrape data...")
        
        print("\n=== Starting Data Scraping ===")
        scrape_youtube_data(driver)
        print("✓ Data scraping completed!")
        
        print("\n" + "="*50)
        print("STEP 2: LOGIN TO YOUR NEW YOUTUBE ACCOUNT")
        print("="*50)
        print("Please login to your NEW YouTube account in the browser.")
        print("Make sure you're fully logged in before proceeding.")
        input("Press Enter when you're logged in and ready to migrate data...")
        
        print("\n=== Starting Data Migration ===")
        migrate_youtube_data(driver)
        print("✓ Data migration completed!")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        return False
    except Exception as e:
        print(f"\n✗ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("\n=== Cleaning Up ===")
        try:
            driver.quit()
            print("✓ Browser closed")
        except:
            print("! Browser was already closed")

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    
    success = main()
    
    if success:
        print("\n🎉 YouTube data migration completed successfully!")
    else:
        print("\n❌ Migration process failed or was interrupted.")
    
    print("\nPress Enter to exit...")
    input()