from selenium import webdriver 
from selenium.webdriver.common.by import By
import time 
import json 
import os

def manual_subscription_scraper(driver):
    """
    Interactive scraper that helps you find the right selectors manually
    """
    print("\n=== MANUAL SUBSCRIPTION SCRAPER ===")
    print("This will help you find subscriptions interactively")
    
    # Navigate to subscriptions page
    driver.get("https://www.youtube.com/feed/channels")
    time.sleep(5)
    
    print("\n1. Current page:", driver.current_url)
    print("2. Can you see your subscriptions on this page? (y/n)")
    
    can_see = input().lower()
    
    if can_see != 'y':
        print("\nTrying alternative URLs...")
        alternative_urls = [
            "https://www.youtube.com/feed/subscriptions",
            "https://www.youtube.com/feed/subscriptions?view=2",  # Grid view
        ]
        
        for url in alternative_urls:
            print(f"\nTrying: {url}")
            driver.get(url)
            time.sleep(5)
            print("Can you see subscriptions now? (y/n)")
            if input().lower() == 'y':
                break
    
    print("\n=== FINDING SELECTORS ===")
    print("We'll try to find subscription links automatically...")
    
    # Try to find all links that might be subscriptions
    all_links = driver.find_elements(By.TAG_NAME, "a")
    subscription_links = []
    
    for link in all_links:
        try:
            href = link.get_attribute("href")
            if href and (("/channel/" in href) or ("/@" in href)):
                # Get the text to help identify
                text = link.text.strip()
                if text and href not in [sub['url'] for sub in subscription_links]:
                    subscription_links.append({
                        'url': href,
                        'text': text,
                        'element': link
                    })
        except:
            continue
    
    print(f"\nFound {len(subscription_links)} potential subscription links:")
    
    # Show first 10 for verification
    for i, sub in enumerate(subscription_links[:10]):
        print(f"{i+1}. {sub['text']} -> {sub['url']}")
    
    if subscription_links:
        print(f"\nDoes this look like your subscriptions? (y/n)")
        if input().lower() == 'y':
            # Extract just the URLs
            urls = [sub['url'] for sub in subscription_links]
            return urls
    
    print("\n=== BROWSER INSPECTION METHOD ===")
    print("Let's try browser inspection:")
    print("1. Right-click on any subscription channel name")
    print("2. Select 'Inspect Element'")
    print("3. Look for the <a> tag with href containing '/channel/' or '/@'")
    print("4. Note the CSS selector path")
    
    print("\nTry these common selectors manually:")
    test_selectors = [
        "ytd-channel-renderer #main-link",
        "ytd-channel-renderer a",
        "#channel-title",
        "a#channel-title",
        "ytd-grid-channel-renderer a",
        ".ytd-channel-name a"
    ]
    
    for selector in test_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"'{selector}': {len(elements)} elements")
            if elements and len(elements) > 3:  # Likely found subscriptions
                links = []
                for elem in elements:
                    href = elem.get_attribute("href")
                    if href and (("/channel/" in href) or ("/@" in href)):
                        links.append(href)
                if links:
                    print(f"  ✓ This selector found {len(links)} subscription URLs!")
                    return links
        except:
            continue
    
    print("\n❌ Automatic detection failed.")
    print("Manual steps:")
    print("1. Open browser dev tools (F12)")
    print("2. Use Console tab")
    print("3. Try this JavaScript:")
    print("   Array.from(document.querySelectorAll('a[href*=\"/channel/\"], a[href*=\"/@\"]')).map(a => a.href)")
    print("4. Copy the results and paste them when prompted")
    
    print("\nWould you like to paste subscription URLs manually? (y/n)")
    if input().lower() == 'y':
        print("Paste the URLs (one per line, empty line to finish):")
        manual_urls = []
        while True:
            url = input().strip()
            if not url:
                break
            if "/channel/" in url or "/@" in url:
                manual_urls.append(url)
        return manual_urls
    
    return []

# Integration function for your main scraper
def scrape_youtube_data(driver):
    data = {"subscriptions": [], "watch_later": []}
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    print("=== SUBSCRIPTION SCRAPING ===")
    
    # Try automatic first
    driver.get("https://www.youtube.com/feed/channels")
    time.sleep(5)
    
    # Quick automatic attempt
    quick_selectors = [
        "ytd-channel-renderer #main-link",
        "ytd-channel-renderer a[href*='/channel/']",
        "a#channel-title"
    ]
    
    for selector in quick_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                for elem in elements:
                    href = elem.get_attribute("href")
                    if href and (("/channel/" in href) or ("/@" in href)):
                        if href not in data["subscriptions"]:
                            data["subscriptions"].append(href)
        except:
            continue
    
    # If automatic failed, try manual
    if not data["subscriptions"]:
        print("Automatic scraping failed. Trying manual method...")
        manual_subs = manual_subscription_scraper(driver)
        data["subscriptions"] = manual_subs
    
    print(f"Subscriptions found: {len(data['subscriptions'])}")
    
    # Watch later scraping (your working code)
    print("\n=== WATCH LATER SCRAPING ===")
    driver.get("https://www.youtube.com/playlist?list=WL")
    time.sleep(5)
    
    # Scroll to load all videos
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    videos = driver.find_elements(By.CSS_SELECTOR, "a#video-title")
    for vid in videos:
        try:
            link = vid.get_attribute("href")
            if link and "/watch?v=" in link:
                if link not in data["watch_later"]:
                    data["watch_later"].append(link)
        except:
            continue
    
    print(f"Watch later videos: {len(data['watch_later'])}")
    
    # Save data
    with open("data/youtube-data.json", "w") as f:
        json.dump(data, f, indent=4)

    print(f'\nData saved to youtube-data.json')
    print(f'Subscriptions: {len(data["subscriptions"])}')
    print(f'Watch Later: {len(data["watch_later"])}')
    
    return data