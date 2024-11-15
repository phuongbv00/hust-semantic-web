pages = {
    'Apple':[
        'https://www.gsmarena.com/apple-phones-48.php',
        'https://www.gsmarena.com/apple-phones-f-48-0-p2.php',
        'https://www.gsmarena.com/apple-phones-f-48-0-p3.php',
    ],
    'Samsung':[
        'https://www.gsmarena.com/samsung-phones-9.php',
        'https://www.gsmarena.com/samsung-phones-f-9-0-p2.php',
        'https://www.gsmarena.com/samsung-phones-f-9-0-p3.php'
    ],
    'Huawei':[
        'https://www.gsmarena.com/huawei-phones-58.php',
        'https://www.gsmarena.com/huawei-phones-f-58-0-p2.php',
        'https://www.gsmarena.com/huawei-phones-f-58-0-p3.php'
    ],
    'LG':[
        'https://www.gsmarena.com/lg-phones-20.php',
        'https://www.gsmarena.com/lg-phones-f-20-0-p2.php',
        'https://www.gsmarena.com/lg-phones-f-20-0-p3.php'
    ],
    'Nokia':[
        'https://www.gsmarena.com/nokia-phones-1.php',
        'https://www.gsmarena.com/nokia-phones-f-1-0-p2.php',
        'https://www.gsmarena.com/nokia-phones-f-1-0-p3.php'
    ],
    'Xiaomi':[
        'https://www.gsmarena.com/xiaomi-phones-80.php',
        'https://www.gsmarena.com/xiaomi-phones-f-80-0-p2.php',
        'https://www.gsmarena.com/xiaomi-phones-f-80-0-p3.php'
    ],
    'Google':[
        'https://www.gsmarena.com/google-phones-107.php'
        ]
}
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import json
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import tempfile
import time

# Read existing product names to skip those already processed
existing_products = set()
json_file = "output_data.json"
existing_data = []

# Load existing data from the JSON file if it exists
if os.path.exists(json_file):
    with open(json_file, mode='r', encoding='utf-8') as file:
        existing_data = json.load(file)
        for item in existing_data:
            product_name = item.get("PRODUCT_NAME")
            if product_name:
                existing_products.add(product_name)

def create_driver():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    return webdriver.Chrome(options=options)

# Define a function to process each URL
def process_url(data, temp_file_path):
    branch, url = data
    driver = create_driver()
    wait = WebDriverWait(driver, 10)
    all_data = []  # Initialize an empty list to store all data objects

    try:
        driver.get(url)
        review_body = wait.until(EC.presence_of_element_located((By.ID, "review-body")))
        links = wait.until(lambda driver: review_body.find_elements(By.TAG_NAME, "a")) 
    except Exception as e:
        print(f"Error loading page {url}")
        driver.quit()
        return
    product_hrefs = []
    for link in links:
        # Chờ để tìm thấy phần tử có thẻ strong chứa tên sản phẩm
        product_name = wait.until(lambda driver: link.find_element(By.TAG_NAME, "strong")).text
        # Lấy href từ link
        href = link.get_attribute("href")
        # Thêm cặp product_name và href vào danh sách
        product_hrefs.append((product_name, href))
    for product_name, href in product_hrefs:
        try:
            if product_name in existing_products:
                continue
            print(href)
            driver.get(href)
            specs_list = wait.until(lambda driver: driver.find_element(By.ID, "specs-list"))
            tables = wait.until(lambda driver: specs_list.find_elements(By.TAG_NAME, "table"))
            data = {"PRODUCT_NAME": product_name, "BRANCH": branch}

            for table in tables:
                key = wait.until(lambda driver: table.find_element(By.TAG_NAME, "th"))
                tr_list = wait.until(lambda driver: table.find_elements(By.TAG_NAME, "tr"))
                master_key = key.text
                sub_data = {}
                previous_subkey = ''
                for tr in tr_list:
                    if tr.text != "":
                        td_list = wait.until(lambda driver: tr.find_elements(By.TAG_NAME, "td"))
                        subkey = td_list[0].text
                        subvalue = td_list[1].text
                        if subkey == '' or subkey == " ":
                            if master_key.lower() == 'network':
                                sub_data[previous_subkey] = sub_data[previous_subkey] + ";" + subvalue
                            else:
                                sub_data["OTHER"] = subvalue
                        else:
                            sub_data[subkey] = subvalue
                            previous_subkey = subkey
                        data[master_key] = sub_data

            all_data.append(data)  # Add data object to all_data list
            time.sleep(10)
            print(f"Success Link :{href}")
        except Exception as e:
            print(f"An error occurred for link {link}")
            continue

    # Save all_data to the temporary file
    with open(temp_file_path, "w", encoding="utf-8") as temp_file:
        json.dump(all_data, temp_file, ensure_ascii=False, indent=4)

    driver.quit()

# Flatten the URLs with their corresponding branches
urls_with_branches = [(branch, url) for branch, urls in pages.items() for url in urls]
# Create a list to store paths of temporary files for each thread
temp_files = []

# Run each (branch, url) tuple in a separate thread
with ThreadPoolExecutor(max_workers=3) as executor:  # Adjust max_workers as needed
    futures = []
    for data in urls_with_branches:
        # Create a temporary file for each thread
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
        temp_files.append(temp_file.name)
        # Submit the process_url function with temp_file.name
        futures.append(executor.submit(process_url, data, temp_file.name))
    
    # Wait for all threads to complete
    for future in as_completed(futures):
        future.result()

# Combine existing data and data from all temporary JSON files into one

combined_data = existing_data
for temp_file_path in temp_files:
    with open(temp_file_path, "r", encoding="utf-8") as temp_file:
        temp_data = json.load(temp_file)
        combined_data.extend(temp_data)
    # Remove the temporary file after reading
    os.remove(temp_file_path)

# Write combined data to the final JSON file
with open("output_data.json", "w", encoding="utf-8") as json_file:
    json.dump(combined_data, json_file, ensure_ascii=False, indent=4)
