from selenium import webdriver
from selenium.webdriver.common.by import By
from flask import Flask, request
import os
import logging
import json

app = Flask(__name__)

@app.route('/')
def hello():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--remote-debugging-port=9230')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument("--window-size=1920,1080")
    options.binary_location = '/usr/local/bin/google-chrome'

    # Specify the path to the ChromeDriver executable
    driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=options)
    driver.get("https://smart.poems.com.sg/smartpark/")
    main_div = driver.find_element(By.CSS_SELECTOR, "div[class='cpark']").find_element(By.CSS_SELECTOR, "div[class='boxedcontent']")
    main_block = main_div.find_element(By.CSS_SELECTOR, "div[class='mob']")
    sgd_rate = main_block.find_element(By.XPATH, ".//p[5]").text.split(" ")[1]
    usd_rate = main_block.find_element(By.XPATH, ".//p[6]").text.split(" ")[1]
    disclaimer = main_block.find_element(By.XPATH, ".//p[7]").text.replace("\n", " ")
    main_block_text = {
        "sgd_rate": sgd_rate,
        "usd_rate": usd_rate,
        "disclaimer": disclaimer
    }
    driver.stop_client()
    driver.close()
    driver.quit()

    return json.dumps(main_block_text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
