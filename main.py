from selenium import webdriver
from flask import Flask, request
import os
import logging

app = Flask(__name__)

@app.route('/')
def hello():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--remote-debugging-port=9230')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-data-dir=/tmp/user-data')
    options.add_argument('--data-path=/tmp/data-path')
    options.add_argument('--homedir=/tmp')
    options.add_argument('--disk-cache-dir=/tmp/cache-dir')
    options.add_argument('--single-process')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--no-zygote')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-breakpad')
    options.add_argument('--disable-client-side-phishing-detection')
    options.add_argument('--disable-component-update')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-domain-reliability')
    options.add_argument('--disable-features=AudioServiceOutOfProcess')
    options.add_argument('--disable-hang-monitor')
    options.add_argument('--disable-ipc-flooding-protection')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-prompt-on-repost')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-sync')
    options.add_argument('--force-color-profile=srgb')
    options.add_argument('--metrics-recording-only')
    options.add_argument('--no-first-run')
    options.add_argument('--safebrowsing-disable-auto-update')
    options.add_argument('--enable-automation')
    options.add_argument('--password-store=basic')
    options.add_argument('--use-mock-keychain')
    options.binary_location = '/usr/local/bin/google-chrome'

    # Specify the path to the ChromeDriver executable
    driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=options)
    driver.get("https://smart.poems.com.sg/smartpark/")
    title = driver.title
    driver.quit()

    return f"The title of the page is: {title}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
