import json
import time

def migrate_youtube_data(driver):
    with open("data/youtube-data.json", "r") as f:
        data = json.load(f)

    # Subscribe to channels
    for channel in data["subscriptions"]:
        driver.get(channel)
        time.sleep(3)
        try:
            sub_button = driver.find_element("xpath", '//ytd-subscribe-button-renderer//tp-yt-paper-button')
            if sub_button.text.lower() == "subscribe":
                sub_button.click()
                print(f"Subscribed to {channel}")
            time.sleep(2)
        except Exception as e:
            print(f"Error subscribing to {channel}: {e}")

    # Add to Watch Later
    for video in data["watch_later"]:
        driver.get(video)
        time.sleep(3)
        try:
            save_button = driver.find_element("xpath", '//ytd-toggle-button-renderer[1]//button')
            save_button.click()
            time.sleep(1)
            watch_later_option = driver.find_element("xpath", '//ytd-menu-service-item-renderer[contains(.,"Watch later")]')
            watch_later_option.click()
            print(f"Added to Watch Later: {video}")
            time.sleep(2)
        except Exception as e:
            print(f"Error saving {video}: {e}")
