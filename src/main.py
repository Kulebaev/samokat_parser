from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from postgres_functions import db_connection, get_category_id, create_data_category, create_table_categories_data
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

TABLE_NAME_CATEGORIES = 'categories'
TABLE_NAME_CATEGORY_LINKS = 'category_links'
TABLE_NAME_PRODUCT_CATEGORIES = 'product_categories'
TABLE_NAME_PRODUCTS = 'products'
URL = 'https://web.samokat.ru'
USER_AGENT = (f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' 
                         f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36')

HEADERS = {
    'User-Agent': USER_AGENT,
}

GOOGLEDRIVER_PATH = '/usr/local/bin/chromedriver'

app = Flask(__name__)

@app.route('/')
def samokat_test():
    product_page = 0
    if 'items' in request.args:
        product_page = request.args['items']
        print(product_page)
        if not product_page.isnumeric():
            return jsonify({'error': 'Параметр "items" должен быть числом.'}), 400
    print(product_page)   
    return main_function(int(product_page))


def main_function(product_page):
    all_category_links = get_all_links()

    links_category = get_links_category(all_category_links, URL)
    
    return get_products(links_category, product_page)


def get_products(links_category, product_page):
    count = 0
    conn =  db_connection()

    for link in links_category:
        if product_page < count:
            break
        driver = run_driver_chrome(link)
        page_source = driver.page_source
        samokat_soup = BeautifulSoup(page_source, 'html.parser')

        divs = samokat_soup.find_all('div', {'class': 'CategorySection_root__6Ai7Z'})

        for div in divs:
            try:
                span_text_category = div.find('span').text

                create_data_category(conn , span_text_category, TABLE_NAME_PRODUCT_CATEGORIES)

                div_products = div.find_all('div', {'class': 'ProductCard_name__czrVx'})
                category_id = get_category_id(conn, span_text_category, TABLE_NAME_PRODUCT_CATEGORIES)
                for div_product in div_products:
                    table_value = div_product.find('span').text

                    create_table_categories_data(conn, category_id, table_value,
                                                TABLE_NAME_PRODUCT_CATEGORIES, TABLE_NAME_PRODUCTS)
            except:
                continue
        if product_page != 0:
            count += 1
        
    driver.close()
    driver.quit() 

    return 'Парсинг сайта завершен'


def run_driver_chrome(url):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument('--start-maximized')

    # Заголовок User-Agent
    options.add_argument(USER_AGENT)
    options.add_argument('accept-language=ru-RU,ru;q=0.9')

    service = Service(executable_path=GOOGLEDRIVER_PATH)

    driver = webdriver.Chrome(options=options,
                              service=service)


    driver.get(url)
    
    return driver


def get_all_links():
    driver = run_driver_chrome(URL)
    links_dict = {}
    try:
        page_source = driver.page_source
        
        # Создаём объект soup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Находим все интересуюище нас div
        divs_with_class = soup.find_all('div', {'class': 'CategoriesGrid_block__9i7qM'})

        for page in divs_with_class:
            list_pages = []
            links = page.find_all('a')

            for a in links:
                link = a.get('href')
                if link:
                    list_pages.append(link)
            links_dict[page.find('span').text] = list_pages
    except Exception as e:
        return {}
    
    driver.close()
    driver.quit() 
    return links_dict
    

def get_links_category(links_category, url):
    links_list = []
    conn =  db_connection()
    for category, links in links_category.items():
        create_data_category(conn , category, TABLE_NAME_CATEGORIES)
        category_id = get_category_id(conn, category, TABLE_NAME_CATEGORIES)
        for link in links:
            create_table_categories_data(conn, category_id, link,
                                         TABLE_NAME_CATEGORIES, TABLE_NAME_CATEGORY_LINKS)
            links_list.append(f'{url}{link}')

    conn.close()

    return links_list


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)