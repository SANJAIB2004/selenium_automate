from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
from datetime import datetime
import msvcrt
import sys

# Windows-compatible timeout for QR code input
def wait_for_input_with_timeout(timeout):
    print(f"Scan QR Code within {timeout} seconds, then press Enter (or press any key to skip)")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if msvcrt.kbhit():
            msvcrt.getch()
            return True
        time.sleep(0.1)
    return False

# User inputs
product_name = input("Enter product to search (e.g., wireless headphones): ")
price_threshold = float(input("Enter price threshold for notification (e.g., 50.0): "))
whatsapp_contact = input("Enter WhatsApp contact name (as saved in your phone): ")

# Set up Chrome driver
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--disable-notifications')  # Avoid pop-ups
driver = webdriver.Chrome(service=service, options=options)

try:
    # Step 1: Search Amazon
    driver.get("https://www.amazon.in")  # Using amazon.in; change to amazon.com if needed

    # Wait for the search bar
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
    )
    print("Search bar found.")

    # Search for the product
    search_box.send_keys(product_name, Keys.RETURN)
    print(f"Searched for: {product_name}")

    # Wait for search results
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.s-main-slot div.s-result-item"))
    )
    print("Search results loaded.")

    # Find the first valid product (skip ads)
    products = driver.find_elements(By.CSS_SELECTOR, "div.s-main-slot div.s-result-item[data-component-type='s-search-result']")
    if not products:
        raise Exception("No valid product results found.")
    print(f"Found {len(products)} product results.")

    first_product = products[0]

    # Extract details with fallback selectors
    try:
        # Try CSS selector first, then XPATH
        try:
            title = first_product.find_element(By.CSS_SELECTOR, "h2 a span").text.strip()
        except:
            title = first_product.find_element(By.XPATH, ".//h2//span").text.strip()
        print("Title extracted successfully.")
    except:
        title = "N/A"
        print("Title not found.")

    try:
        price_whole = first_product.find_element(By.CSS_SELECTOR, "span.a-price-whole").text
        price = float(price_whole.replace("₹", "").replace(",", ""))
        print("Price extracted successfully.")
    except:
        price = "N/A"
        print("Price not found.")

    try:
        rating = first_product.find_element(By.CSS_SELECTOR, "span.a-icon-alt").text
        print("Rating extracted successfully.")
    except:
        try:
            rating = first_product.find_element(By.CSS_SELECTOR, "i.a-icon-star span").text
            print("Rating extracted via fallback selector.")
        except:
            rating = "N/A"
            print("Rating not found.")

    # Print extracted data
    print(f"Product: {title}")
    print(f"Price: {price}")
    print(f"Rating: {rating}")

    # Save to CSV
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("price_tracker.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(["Timestamp", "Product", "Price", "Rating"])
        writer.writerow([timestamp, title, price, rating])
    print("Data saved to CSV.")

    # Step 2: Send WhatsApp notification if price is below threshold
    if isinstance(price, float) and price < price_threshold:
        print(f"Price ({price}) is below threshold ({price_threshold}). Sending WhatsApp notification...")
        
        # Prepare message
        message = f"Price Alert! {title} is now ₹{price} (below ₹{price_threshold}). Rating: {rating}"

        # Open WhatsApp Web
        driver.get("https://web.whatsapp.com")
        
        # Wait for QR code scan with timeout
        if wait_for_input_with_timeout(30):
            try:
                input()  # Wait for Enter after scanning
                print("Logged In")
            except KeyboardInterrupt:
                print("Skipping WhatsApp notification.")
                raise
        else:
            print("Skipping WhatsApp notification due to timeout.")
            raise Exception("QR code scan timed out.")

        # Search for contact
        search_box = WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.XPATH, "//div[@title='Search input textbox']"))
        )
        search_box.click()
        time.sleep(1)
        search_box.send_keys(whatsapp_contact)
        time.sleep(2)
        print(f"Searched for contact: {whatsapp_contact}")

        # Select the contact
        try:
            selected_contact = driver.find_element(By.XPATH, f"//span[@title='{whatsapp_contact}']")
            selected_contact.click()
            print("Contact selected.")
        except:
            print(f"Contact '{whatsapp_contact}' not found.")
            raise

        # Send the message
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@title='Type a message']"))
        )
        message_box.send_keys(message, Keys.ENTER)
        time.sleep(2)
        print("WhatsApp message sent successfully.")

except Exception as e:
    print(f"Error: {e}")
    print("Page source for debugging:")
    print(driver.page_source[:1000])
    sys.exit(1)

finally:
    driver.quit()