from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import xlsxwriter
from flask import Flask, request
import time
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

    # Specify the path to the ChromeDriver executable
    driver = webdriver.Chrome(options=options)
    return scrape_page_fast(driver, location, start_page, item_count)

def scrape_page_fast(driver, location, start_page, item_count):
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
            if (item_count > count + 20) :
                count_now = 20
            else:
                count_now = item_count - count
            for i in range(1, count_now + 1, 1):
                try:
                    print(f"get {count} - {i}")
                    # driver.refresh()
                    section = driver.find_element(By.CSS_SELECTOR, "body").find_element(By.CSS_SELECTOR, "div[class='listing-portion']")
                    section = section.find_element(By.CSS_SELECTOR, "div[class='listings']").find_element(By.CSS_SELECTOR, "div[class='container']")
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

def scrape_page(driver, location, start_page, worksheet):
    driver.get(ROOT)
    time.sleep(3)                                               
    section = driver.find_element(By.CSS_SELECTOR, "body").find_element(By.CSS_SELECTOR, "div[class='listing-portion']")
    section = section.find_element(By.CSS_SELECTOR, "div[class='listings']").find_element(By.CSS_SELECTOR, "div[class='container']")
    section.find_element(By.XPATH, ".//div[4]/app-flat-cards-categories").click()
    time.sleep(3)
    driver.find_element(By.XPATH, ".//app-search-filter/form/div/div/div/div").click() # Click Location Dropdown
    driver.find_element(By.XPATH, ".//app-search-filter/form/div/div/div/div/div[@id='searchWrapper']/div[@id='address']").click()
    driver.find_element(By.XPATH, ".//app-search-filter/form/div/div/div/div/div/div/div/input").send_keys(location)
    driver.find_element(By.XPATH, ".//app-search-filter/form/div/div/div/div/div/div/div/input").send_keys(Keys.ENTER)
    
    worksheet.write(0, 0, "Address")
    worksheet.write(0, 1, "Address_2")
    worksheet.write(0, 2, "Price")
    worksheet.write(0, 3, "Flat Type")
    worksheet.write(0, 4, "Flat Area")
    worksheet.write(0, 5, "Recent Low")
    worksheet.write(0, 6, "Recent High")
    worksheet.write(0, 7, "Price relative to Recent High")
    worksheet.write(0, 8, "Town")
    worksheet.write(0, 9, "Storey")
    worksheet.write(0, 10, "Remaining Lease")
    worksheet.write(0, 11, "Number of bathrooms")
    worksheet.write(0, 12, "Number of bedrooms")
    worksheet.write(0, 13, "Balcony")
    worksheet.write(0, 14, "Contra")
    worksheet.write(0, 15, "Extension of stay")
    worksheet.write(0, 16, "Upgrading")
    worksheet.write(0, 17, "Ethnic Eligibility")
    worksheet.write(0, 18, "SPR Eligibility")
    worksheet.write(0, 19, "Agent Listing?")
    worksheet.write(0, 20, "Link to property")
    count = (start_page - 1) * 20 + 1
    next_exists = True
    
    for i in range(1, start_page, 1):
        try:
        # Click "Right" button
            section = driver.find_element(By.CSS_SELECTOR, "body").find_element(By.CSS_SELECTOR, "div[class='listing-portion']")
            section = section.find_element(By.CSS_SELECTOR, "div[class='listings']").find_element(By.CSS_SELECTOR, "div[class='container']")
                
            section.find_element(By.XPATH, ".//div[5]/div/nav/ngb-pagination/ul/li[last()-1]").click()
        except Exception as e:
            print(e)
            break

    while next_exists:
        try:
            for i in range(1, 21, 1):
                try:
                    print(f"get {count} - {i}")
                    # driver.refresh()
                    section = driver.find_element(By.CSS_SELECTOR, "body").find_element(By.CSS_SELECTOR, "div[class='listing-portion']")
                    section = section.find_element(By.CSS_SELECTOR, "div[class='listings']").find_element(By.CSS_SELECTOR, "div[class='container']")
                    item = section.find_element(By.XPATH, f".//div[4]/app-flat-cards[{i}]")
                    subpage_link = item.find_element(By.XPATH, ".//div/div/div/div/div[2]/div/a").get_attribute("href")
                    print(subpage_link)
                    # Open a new window 
                    driver.execute_script("window.open('');") 
                    
                    # Switch to the new window and open new URL 
                    driver.switch_to.window(driver.window_handles[1]) 
                    driver.get(subpage_link) 
                    time.sleep(2)
                    in_subpage = True
                    scrape_individual(driver, count, worksheet)

                    # Closing new_url tab 
                    driver.close() 
                    
                    # Switching to old tab 
                    driver.switch_to.window(driver.window_handles[0]) 
                    time.sleep(2)
                    in_subpage = False
                    count = count + 1
                except Exception as e:
                    print("IN")
                    print(e)
                    print(f"Skipped {count} - {i}")
                    if in_subpage:
                        # Closing new_url tab 
                        driver.close() 
                    
                    # Switching to old tab 
                        driver.switch_to.window(driver.window_handles[0]) 
                        in_subpage = False
                    time.sleep(10)
                

        # Click "Right" button
            section = driver.find_element(By.CSS_SELECTOR, "body").find_element(By.CSS_SELECTOR, "div[class='listing-portion']")
            section = section.find_element(By.CSS_SELECTOR, "div[class='listings']").find_element(By.CSS_SELECTOR, "div[class='container']")
                
            section.find_element(By.XPATH, ".//div[5]/div/nav/ngb-pagination/ul/li[8]").click()
            
        except Exception as e:
            print("END")
            print(e)
            break

def scrape_individual(driver, count, worksheet):
    section = driver.find_element(By.CSS_SELECTOR, "app-resale-flat-details").find_element(By.CSS_SELECTOR, "div[class='flat-details']")
    top_block = section.find_element(By.CSS_SELECTOR, "div[class='border-bottom']")
    add_price = top_block.find_element(By.CSS_SELECTOR, "app-overview").find_element(By.XPATH, ".//div[1]")
    add_block = add_price.find_element(By.XPATH, ".//div[1]")
    worksheet.write(count, 20, driver.current_url)
    address = add_block.find_element(By.CSS_SELECTOR, "h3").text
    worksheet.write(count, 0, address)
    address_2 = add_block.find_element(By.CSS_SELECTOR, "h5").text
    worksheet.write(count, 1, address_2)
    details = add_block.find_element(By.CSS_SELECTOR, "p").text.splitlines()
    flat_type = details[0]
    flat_area = details[1]
    worksheet.write(count, 3, flat_type)
    worksheet.write(count, 4, flat_area)

    # /div[@class='flat-details']/div[@class='border-bottom']/app-overview/div[1]
    price_block = add_price.find_element(By.XPATH, ".//div[2]/div/div")
    price = int(price_block.find_element(By.CSS_SELECTOR, "h2").text[1:].replace(',', ''))
    worksheet.write(count, 2, price)

    bottom_block = section.find_element(By.CSS_SELECTOR, "div[class='container my-10']")
    info_block = bottom_block.find_element(By.XPATH, ".//app-key-details/div/div")
    town = info_block.find_element(By.XPATH, ".//div/div[4]").text.splitlines()[1]
    storey = info_block.find_element(By.XPATH, ".//div/div[5]").text.splitlines()[1]
    rem_lease = info_block.find_element(By.XPATH, ".//div/div[6]").text.splitlines()[1]
    bathroom = info_block.find_element(By.XPATH, ".//div/div[7]").text.splitlines()[1]
    bedroom = info_block.find_element(By.XPATH, ".//div/div[8]").text.splitlines()[1]
    balcony = info_block.find_element(By.XPATH, ".//div/div[9]").text.splitlines()[1]
    contra = info_block.find_element(By.XPATH, ".//div/div[10]").text.splitlines()[1]
    extension = info_block.find_element(By.XPATH, ".//div/div[11]").text.splitlines()[1]
    upgrading = info_block.find_element(By.XPATH, ".//div/div[12]").text.splitlines()[1]
    ethnic = info_block.find_element(By.XPATH, ".//div/div[13]").text.splitlines()[1]
    spr = info_block.find_element(By.XPATH, ".//div/div[14]").text.splitlines()[1]
    worksheet.write(count, 8, town)
    worksheet.write(count, 9, storey)
    worksheet.write(count, 10, rem_lease)
    worksheet.write(count, 11, int(bathroom))
    worksheet.write(count, 12, int(bedroom))
    worksheet.write(count, 13, balcony)
    worksheet.write(count, 14, contra)
    worksheet.write(count, 15, extension)
    worksheet.write(count, 16, upgrading)
    worksheet.write(count, 17, ethnic)
    worksheet.write(count, 18, spr)
    price_range = info_block.find_element(By.XPATH, ".//div[3]/div[3]").text.splitlines()[1]
    if price_range.startswith("No"):
        worksheet.write(count, 5, "N/A")
        worksheet.write(count, 6, "N/A")
        worksheet.write(count, 7, "0")
    else:
        floor = int(price_range.split(' ')[0][1:].replace(',', ''))
        ceil = int(price_range.split(' ')[2][1:].replace(',', ''))
        worksheet.write(count, 5, floor)
        worksheet.write(count, 6, ceil)
        percentile = (price / ceil) * 100
        worksheet.write(count, 7, percentile)
    
    description_block = info_block.find_element(By.XPATH, ".//div[2]/div/div[2]/div/div/div/div")
    description_block.find_element(By.XPATH, ".//div[2]").click()

    agent_text = description_block.find_element(By.XPATH, ".//div/div").text
    if 'CEA' in agent_text:
        worksheet.write(count, 19, "Agent")
    else:
        worksheet.write(count, 19, "Non-Agent")

def get_data_fast(start_page, item_count, location):
    try:
        options = webdriver.ChromeOptions()
        new_options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Chrome(options=options)
        data = scrape_page_fast(driver, location, start_page, item_count)
    finally:
        return data

# Start should be 20*k + 1, where k is an integer
#data = get_data_fast(1, 10, "anchorvale")
#print(data)

if __name__ == "__main__":
    port = 5000
    app.run(host='0.0.0.0', port=port)