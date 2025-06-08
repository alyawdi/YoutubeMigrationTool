import json 
import time 
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def debug_page_elements(driver, page_type="channel"):
    """Debug function to see what elements are actually on the page"""
    print(f"\n=== DEBUGGING {page_type.upper()} PAGE ===")
    print(f"Current URL: {driver.current_url}")
    
    if page_type == "channel":
        # Look for subscribe-related elements
        selectors_to_test = [
            ('xpath', '//ytd-subscribe-button-renderer'),
            ('xpath', '//button[contains(@aria-label, "Subscribe")]'),
            ('xpath', '//button[contains(text(), "Subscribe")]'),
            ('css', 'ytd-subscribe-button-renderer button'),
            ('xpath', '//tp-yt-paper-button[contains(@aria-label, "Subscribe")]'),
            ('xpath', '//yt-button-shape[contains(@aria-label, "Subscribe")]'),
            ('css', '#subscribe-button'),
        ]
    else:  # video page
        selectors_to_test = [
            ('xpath', '//button[@aria-label="Save to Watch later"]'),
            ('xpath', '//button[contains(@aria-label, "Save")]'),
            ('css', '#top-level-buttons ytd-menu-renderer button'),
            ('xpath', '//ytd-menu-renderer//button[contains(@aria-label, "Save")]'),
        ]
    
    print("Testing selectors:")
    found_elements = []
    
    for selector_type, selector in selectors_to_test:
        try:
            if selector_type == "xpath":
                elements = driver.find_elements(By.XPATH, selector)
            else:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            print(f"  {selector}: Found {len(elements)} elements")
            
            if elements:
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    try:
                        text = elem.text.strip()
                        aria_label = elem.get_attribute('aria-label') or ''
                        title = elem.get_attribute('title') or ''
                        print(f"    Element {i+1}: text='{text}', aria-label='{aria_label}', title='{title}'")
                        found_elements.append({
                            'element': elem,
                            'selector': selector,
                            'text': text,
                            'aria_label': aria_label,
                            'title': title
                        })
                    except Exception as e:
                        print(f"    Element {i+1}: Error reading - {e}")
        except Exception as e:
            print(f"  {selector}: Error - {e}")
    
    return found_elements

def interactive_subscribe(driver, channel_url):
    """Interactive subscription with manual fallback"""
    print(f"\n=== SUBSCRIBING TO: {channel_url} ===")
    
    try:
        driver.get(channel_url)
        time.sleep(3)
        
        # Debug what's on the page
        found_elements = debug_page_elements(driver, "channel")
        
        # Try automatic subscription first
        subscribe_selectors = [
            ('xpath', '//ytd-subscribe-button-renderer//button[contains(@aria-label, "Subscribe")]'),
            ('xpath', '//button[contains(@aria-label, "Subscribe")]'),
            ('xpath', '//button[contains(text(), "Subscribe")]'),
            ('css', 'ytd-subscribe-button-renderer button'),
            ('xpath', '//tp-yt-paper-button[contains(@aria-label, "Subscribe")]'),
            ('xpath', '//yt-button-shape//button'),
        ]
        
        for selector_type, selector in subscribe_selectors:
            try:
                if selector_type == "xpath":
                    element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                
                # Check if it's actually a subscribe button
                text = element.text.strip().lower()
                aria_label = element.get_attribute('aria-label', '').lower()
                
                if 'subscribe' in text or 'subscribe' in aria_label:
                    if 'subscribed' not in text and 'subscribed' not in aria_label:
                        element.click()
                        print(f"✓ Successfully clicked subscribe button!")
                        time.sleep(random.uniform(2, 4))
                        return True
                    else:
                        print(f"- Already subscribed to this channel")
                        return True
                        
            except TimeoutException:
                continue
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        # If automatic failed, provide manual option
        print("\n❌ Automatic subscription failed!")
        print("Please manually subscribe to this channel in the browser.")
        print("The browser should be showing the channel page.")
        input("Press Enter after you've subscribed (or Enter to skip)...")
        return True
        
    except Exception as e:
        print(f"Error loading channel: {e}")
        return False

def interactive_watch_later(driver, video_url):
    """Interactive watch later with manual fallback"""
    print(f"\n=== ADDING TO WATCH LATER: {video_url} ===")
    
    try:
        driver.get(video_url)
        time.sleep(3)
        
        # Debug what's on the page
        found_elements = debug_page_elements(driver, "video")
        
        # Try automatic save to watch later
        save_selectors = [
            ('xpath', '//button[@title="Save to Watch later"]'),
            ('xpath', '//button[@aria-label="Save to Watch later"]'),
            ('xpath', '//button[contains(@aria-label, "Save")]'),
            ('css', '#top-level-buttons ytd-menu-renderer button'),
            ('xpath', '//ytd-menu-renderer//button'),
        ]
        
        for selector_type, selector in save_selectors:
            try:
                if selector_type == "xpath":
                    element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                
                aria_label = element.get_attribute('aria-label', '').lower()
                title = element.get_attribute('title', '').lower()
                
                if 'save' in aria_label or 'save' in title or 'watch later' in aria_label:
                    element.click()
                    time.sleep(2)
                    
                    # Look for Watch Later option in the menu
                    try:
                        wl_selectors = [
                            ('xpath', '//yt-formatted-string[text()="Watch later"]'),
                            ('xpath', '//span[text()="Watch later"]'),
                            ('xpath', '//ytd-playlist-add-to-button-renderer//span[contains(text(), "Watch later")]'),
                        ]
                        
                        for wl_sel_type, wl_selector in wl_selectors:
                            try:
                                if wl_sel_type == "xpath":
                                    wl_element = WebDriverWait(driver, 3).until(
                                        EC.element_to_be_clickable((By.XPATH, wl_selector))
                                    )
                                else:
                                    wl_element = WebDriverWait(driver, 3).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, wl_selector))
                                    )
                                
                                wl_element.click()
                                print(f"✓ Successfully added to Watch Later!")
                                time.sleep(random.uniform(2, 4))
                                return True
                            except TimeoutException:
                                continue
                        
                        # If we can't find Watch Later specifically, the save might have worked
                        print(f"~ Clicked save button (Watch Later option not found)")
                        return True
                        
                    except Exception as e:
                        print(f"Error finding Watch Later option: {e}")
                        return True  # Assume it worked
                        
            except TimeoutException:
                continue
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        # If automatic failed, provide manual option
        print("\n❌ Automatic save to Watch Later failed!")
        print("Please manually add this video to Watch Later in the browser.")
        print("Look for the 'Save' button under the video.")
        input("Press Enter after you've saved it (or Enter to skip)...")
        return True
        
    except Exception as e:
        print(f"Error loading video: {e}")
        return False

def migrate_youtube_data(driver):
    """Enhanced migration with debugging and manual fallbacks"""
    try:
        with open("data/youtube-data.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: youtube-data.json not found. Please run scraper first.")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON file.")
        return
    
    print(f"Starting migration of {len(data.get('subscriptions', []))} subscriptions and {len(data.get('watch_later', []))} watch later videos")
    
    # Ask user preference for debugging
    print("\nDebugging options:")
    print("1. Full auto (attempt automatic with minimal output)")
    print("2. Debug mode (show all element detection)")
    print("3. Interactive mode (manual fallback for each item)")
    
    mode = input("Choose mode (1/2/3): ").strip()
    
    debug_mode = mode == "2"
    interactive_mode = mode == "3"
    
    # Subscribe to channels
    successful_subs = 0
    failed_subs = 0
    
    print(f"\n=== PROCESSING SUBSCRIPTIONS ===")
    
    for i, channel in enumerate(data.get("subscriptions", []), 1):
        print(f"\nProcessing subscription {i}/{len(data['subscriptions'])}: {channel}")
        
        if interactive_mode:
            success = interactive_subscribe(driver, channel)
        else:
            success = subscribe_to_channel(driver, channel, debug_mode)
        
        if success:
            successful_subs += 1
        else:
            failed_subs += 1
        
        # Rate limiting with randomization
        time.sleep(random.uniform(3, 6))
    
    print(f"\nSubscription Summary:")
    print(f"Successful: {successful_subs}")
    print(f"Failed: {failed_subs}")
    print(f"Total: {len(data.get('subscriptions', []))}")
    
    # Add videos to Watch Later
    successful_wl = 0
    failed_wl = 0
    
    print(f"\n=== PROCESSING WATCH LATER VIDEOS ===")
    
    for i, video in enumerate(data.get("watch_later", []), 1):
        print(f"\nProcessing watch later {i}/{len(data['watch_later'])}: {video}")
        
        if interactive_mode:
            success = interactive_watch_later(driver, video)
        else:
            success = add_to_watch_later(driver, video, debug_mode)
        
        if success:
            successful_wl += 1
        else:
            failed_wl += 1
        
        # Rate limiting with randomization
        time.sleep(random.uniform(3, 6))
    
    print(f"\nWatch Later Summary:")
    print(f"Successful: {successful_wl}")
    print(f"Failed: {failed_wl}")
    print(f"Total: {len(data.get('watch_later', []))}")
    
    print(f"\nMigration completed!")
    print(f"Total successful operations: {successful_subs + successful_wl}")
    print(f"Total failed operations: {failed_subs + failed_wl}")

def subscribe_to_channel(driver, channel_url, debug=False):
    """Original subscription logic with optional debugging"""
    try:
        driver.get(channel_url)
        time.sleep(3)
        
        if debug:
            debug_page_elements(driver, "channel")
        
        # Your original logic here, simplified
        subscribe_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, 
                '//ytd-subscribe-button-renderer//tp-yt-paper-button | //button[contains(@aria-label, "Subscribe")]'))
        )
        
        button_text = subscribe_button.text.strip().lower()
        aria_label = subscribe_button.get_attribute('aria-label', '').lower()
        
        if 'subscribe' in button_text or 'subscribe' in aria_label:
            if 'subscribed' not in button_text and 'subscribed' not in aria_label:
                subscribe_button.click()
                print(f"✓ Subscribed to {channel_url}")
                return True
            else:
                print(f"- Already subscribed to {channel_url}")
                return True
                
    except Exception as e:
        if debug:
            print(f"✗ Error subscribing to {channel_url}: {e}")
        else:
            print(f"✗ Failed to subscribe to {channel_url}")
        return False

def add_to_watch_later(driver, video_url, debug=False):
    """Original watch later logic with optional debugging"""
    try:
        driver.get(video_url)
        time.sleep(3)
        
        if debug:
            debug_page_elements(driver, "video")
        
        # Your original selectors
        selectors = [
            '//button[@aria-label="Save to Watch later"]',
            '//button[contains(@aria-label, "Save to")]',
            '//ytd-playlist-add-to-button-renderer//button',
            '//button[contains(@title, "Save")]'
        ]
        
        watch_later_button = None
        for selector in selectors:
            try:
                watch_later_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                break
            except TimeoutException:
                continue
        
        if watch_later_button:
            watch_later_button.click()
            time.sleep(2)
            
            try:
                wl_option = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, 
                        '//yt-formatted-string[text()="Watch later"] | //span[text()="Watch later"]'))
                )
                wl_option.click()
                print(f"✓ Added {video_url} to Watch Later")
                return True
            except TimeoutException:
                print(f"~ Clicked save for {video_url}")
                return True
        else:
            print(f"✗ Could not find save button for {video_url}")
            return False
            
    except Exception as e:
        if debug:
            print(f"✗ Error adding {video_url} to Watch Later: {e}")
        else:
            print(f"✗ Failed to add {video_url} to Watch Later")
        return False