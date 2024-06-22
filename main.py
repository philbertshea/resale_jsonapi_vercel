from selenium import webdriver
from flask import Flask, request
import os
import logging

app = Flask(__name__)

@app.route('/')
def hello():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--start-maximized")
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
