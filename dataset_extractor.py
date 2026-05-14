import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json
import os

def generate_large_ai_dataset(keyword, target_items=100):
    print(f"🚀 [STEP 1] Starting Big Data Extractor for: '{keyword}'")
    options = uc.ChromeOptions()
    # Eager loading taake page jaldi interactable ho jaye
    options.page_load_strategy = 'eager' 
    driver = uc.Chrome(options=options)
    
    # Page load timeout 30 seconds
    driver.set_page_load_timeout(30)
    
    raw_data = []
    current_page = 1
    empty_pages_count = 0 

    try:
        while len(raw_data) < target_items:
            print(f"📄 [STEP 2] Scraping Page {current_page} (Total items extracted so far: {len(raw_data)})...")
            
            formatted_keyword = keyword.replace(" ", "+")
            url = f"https://www.amazon.com/s?k={formatted_keyword}&page={current_page}"
            
            try:
                driver.get(url)
            except TimeoutException:
                print(f"⚠️ Page {current_page} took too long to load! Skipping to next page...")
                current_page += 1
                continue 
            
            time.sleep(5) # Wait for elements to render
            
            # Captcha Check
            if "captcha" in driver.page_source.lower() or "type the characters" in driver.page_source.lower():
                print("🛑 CAPTCHA DETECTED! Please solve it in the browser window within 20 seconds...")
                time.sleep(20)
                
            try:
                products = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
                
                if len(products) == 0:
                    print("⚠️ No products found on this page. Amazon layout might have changed or IP is temporarily restricted.")
                    empty_pages_count += 1
                else:
                    empty_pages_count = 0 
                    print(f"🔍 Found {len(products)} products on this page. Extracting...")
                
                # --- THE SMART EXTRACTOR ---
                for item in products:
                    try:
                        # Title Extraction
                        title_elements = item.find_elements(By.CSS_SELECTOR, "h2")
                        title = title_elements[0].text.strip() if title_elements else ""
                        if not title and title_elements:
                             title = title_elements[0].get_attribute('textContent').strip()

                        # Price Extraction
                        price_elements = item.find_elements(By.CSS_SELECTOR, "span.a-price > span.a-offscreen")
                        price = price_elements[0].get_attribute('textContent').strip() if price_elements else ""
                        
                        # Only add if both title and price are present
                        if title and price:
                            raw_data.append({"title": title, "price": price})
                            
                            if len(raw_data) >= target_items:
                                break
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"⚠️ Error extracting data on Page {current_page}.")
            
            if empty_pages_count >= 3:
                print("⛔ 3 empty pages in a row! Amazon might be blocking us. Stopping extraction to save current data.")
                break

            current_page += 1
            
            # Safety limit
            if current_page > 10:
                print("🛑 Safety limit reached (10 pages). Stopping extraction.")
                break

    finally:
        print("\n🏁 Browser Tasks Completed. Closing Browser...")
        try:
            driver.quit()
        except:
            pass

    # --- DATA CLEANING & AI FORMATTING ---
    if len(raw_data) > 0:
        print(f"🧹 [STEP 3] Cleaning {len(raw_data)} extracted items...")
        
        ai_dataset = []
        for data in raw_data:
            ai_entry = {
                "instruction": "Act as an E-commerce pricing expert. Given the product title, estimate its current market price.",
                "input": f"Product Title: {data['title']}",
                "output": f"The estimated price on Amazon is {data['price']}."
            }
            ai_dataset.append(ai_entry)

        file_name = f"massive_ai_dataset_{keyword.replace(' ', '_')}.json"
        print(f"🧠 [STEP 4] Saving AI-Ready Dataset with {len(ai_dataset)} rows...")
        
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(ai_dataset, f, indent=4)
            
        print(f"🎉 SUCCESS! Massive Dataset saved as '{file_name}'")
       
    else:
        print("❌ Could not extract any data. Please try again later or use a VPN.")

# Run the Bot
generate_large_ai_dataset("Machine Learning Books", target_items=100)

# Force a clean Python exit to prevent WinError 6
os._exit(0)