from selenium import webdriver
from flask import Flask, request
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import os

app = Flask(__name__)

def download_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    #chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--window-size=1920x1080")
    #chrome_options.add_argument('--remote-debugging-port=9222')  # Add this line
    #chrome_options.add_argument('--window-size=1280x1696')
    #chrome_options.add_argument('--user-data-dir=/tmp/user-data')
    #chrome_options.add_argument('--data-path=/tmp/data-path')
    #chrome_options.add_argument('--homedir=/tmp')
    #chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
    chrome_options.binary_location = '/usr/local/bin/google-chrome'
    driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", chrome_options=chrome_options)
    driver.get("https://google.com")
    title = driver.title
    language = driver.find_element(By.XPATH, "//div[@id='SIvCob']").text
    data = {'Page Title': title, 'Language': language}
    return data


@app.route('/', methods = ['GET','POST'])
def home():
    if (request.method == 'GET'):
        return download_selenium()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=os.getenv("PORT", default=5000))
    