import time
import os
from bs4 import BeautifulSoup
from flask import Flask, Response, jsonify, render_template
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


app = Flask(__name__)

@app.route('/')
def test_fullpage_screenshot():
    return test()
    

def test():
    url = "https://web.samokat.ru"
    filename = "samokat.png"

    list_pages = []

    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument('--start-maximized')

    # Установка заголовка User-Agent
    options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' 
                         f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36')
    options.add_argument('accept-language=ru-RU,ru;q=0.9')

    service = Service(executable_path="/usr/local/bin/chromedriver")

    driver = webdriver.Chrome(options=options)
    
    driver.get(url)

    try:
        page_source = driver.page_source
        
        soup = BeautifulSoup(page_source, 'html.parser')
        divs_with_class = soup.find_all('div', {'class': 'CategoriesGrid_block__9i7qM'})

        for page in divs_with_class:
                link = page.find('span')
                list_pages.append(link.text)

    except Exception as e:
        return jsonify({'Ошибка': e})
        

    driver.close()
    driver.quit()
    
    return jsonify({'Ошибка': list_pages})
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)