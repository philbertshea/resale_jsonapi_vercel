from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from flask import Flask, request
import os
import logging
import json

app = Flask(__name__)
ROOT = "https://homes.hdb.gov.sg/home/finding-a-flat"

@app.route('/')
def instructions():
    return "<h1>Using the Resale JSON API</h1><br><p>This API contains two routes: <ol><li>Route 1: '/'. Contains Instructions to API</li><li>Route 2: '/location/start_page/item_count'. Returns JSON response based on three parameters: Location (Use _ as word divider), Start_page (each page contains 20 items. Use 1 as default), Item_count (total number of items to return). </li></ol> For example, to get the closest 50 listings to Anchorvale Village, use /anchorvale_village/1/50. "

@app.route('/<location>/<start_page>/<item_count>')
def hello(start_page=1, item_count=20, location="Anchorvale Village"):
    start_page = int(start_page)
    item_count = int(item_count)
    location = location.replace("_", " ")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--remote-debugging-port=9230')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument("--window-size=1920,1080")
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.binary_location = '/usr/local/bin/google-chrome'

    # Specify the path to the ChromeDriver executable
    driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=options)
    data_array = []
    driver.get(ROOT)                                 
    section = driver.find_element(By.CSS_SELECTOR, "body").find_element(By.CSS_SELECTOR, "div[class='listing-portion']")
    section = section.find_element(By.CSS_SELECTOR, "div[class='listings']").find_element(By.CSS_SELECTOR, "div[class='container']")
    element = section.find_element(By.XPATH, ".//div[4]/app-flat-cards-categories")
    driver.execute_script("arguments[0].click();", element)
    element = driver.find_element(By.XPATH, ".//app-search-filter/form/div/div/div/div")
    driver.execute_script("arguments[0].click();", element) # Click Location Dropdown
    element = driver.find_element(By.XPATH, ".//app-search-filter/form/div/div/div/div/div[@id='searchWrapper']/div[@id='address']/div[2]/ul/li/a")
    driver.execute_script("arguments[0].click();", element)
    driver.find_element(By.XPATH, ".//app-search-filter/form/div/div/div/div/div/div/div/input").send_keys(location)
    driver.find_element(By.XPATH, ".//app-search-filter/form/div/div/div/div/div/div/div/input").send_keys(Keys.ENTER)
    
    count = 0
    
    for i in range(1, start_page, 1):
        try:
        # Click "Right" button
            section = driver.find_element(By.CSS_SELECTOR, "body").find_element(By.CSS_SELECTOR, "div[class='listing-portion']")
            section = section.find_element(By.CSS_SELECTOR, "div[class='listings']").find_element(By.CSS_SELECTOR, "div[class='container']")
                
            element = section.find_element(By.XPATH, ".//div[5]/div/nav/ngb-pagination/ul/li[last()-1]")
            driver.execute_script("arguments[0].click();", element)
        except Exception as e:
            print(e)
            driver.stop_client()
            driver.close()
            driver.quit()
            return json.dumps(data_array)

    while count < item_count:
        try:
            for i in range(1, 21, 1):
                if (count >= item_count):
                    break
                try:
                    print(f"get {count} - {i}")
                    # driver.refresh()
                    section = driver.find_element(By.CSS_SELECTOR, "body").find_element(By.CSS_SELECTOR, "div[class='listing-portion']")
                    section = section.find_element(By.CSS_SELECTOR, "div[class='listings']").find_element(By.CSS_SELECTOR, "div[class='container']")
                    driver.get_screenshot_as_file(f'screenshot{i}.png')
                    item = section.find_element(By.XPATH, f".//div[4]/app-flat-cards[{i}]")
                    item_block = item.find_element(By.XPATH, ".//div/div/div/div/div[2]/div/a")
                    address = item_block.find_element(By.XPATH, ".//div[2]/h2").text
                    flat_type = item_block.find_element(By.XPATH, ".//div[2]/div/div/p").text.split(" ")[2]
                    floor_area = item_block.find_element(By.XPATH, ".//div[2]/div/div/p[2]").text.split(" ")[2]
                    price = item_block.find_element(By.XPATH, ".//div[2]/div/div[2]").text
                    subpage_link = item_block.get_attribute("href")
                    item_dict = {
                        "address": address,
                        "price": price,
                        "flat_type": flat_type,
                        "floor_area": floor_area,
                        "link": subpage_link
                    }
                    data_array.append(item_dict)
                    count = count + 1
                except Exception as e:
                    print(e)
                    print(f"Skipped {count} - {i}")

                
        # Click "Right" button
            section = driver.find_element(By.CSS_SELECTOR, "body").find_element(By.CSS_SELECTOR, "div[class='listing-portion']")
            section = section.find_element(By.CSS_SELECTOR, "div[class='listings']").find_element(By.CSS_SELECTOR, "div[class='container']")
                
            element = section.find_element(By.XPATH, ".//div[5]/div/nav/ngb-pagination/ul/li[last()-1]")
            driver.execute_script("arguments[0].click();", element)
            
        except Exception as e:
            print("END")
            print(e)
            driver.stop_client()
            driver.close()
            driver.quit()
            return json.dumps(data_array)

    driver.stop_client()
    driver.close()
    driver.quit()
    return json.dumps(data_array)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
