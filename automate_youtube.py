from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

# Set up Chrome driver with WebDriver Manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open YouTube
driver.get("https://www.youtube.com")

# Wait for the page to load
time.sleep(2)

# Find the search bar
search_box = driver.find_element(By.NAME, "search_query")

# Enter "retro songs" and submit
search_box.send_keys("retro songs")
search_box.send_keys(Keys.RETURN)

# Wait to see the results
time.sleep(5)

first_video = driver.find_element(By.CSS_SELECTOR, "ytd-video-renderer #video-title")
first_video.click()

time.sleep(60)

# Close the browser
driver.quit()