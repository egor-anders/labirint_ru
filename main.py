import requests
import json
import csv
from datetime import datetime
from bs4 import BeautifulSoup
import time

current_time = datetime.now().strftime('%d_%m_%Y_%H_%M')

def get_html(url):
    headers = {
        'accept':
        'text/html, */*; q=0.01',
        'user-agent':
        'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Mobile Safari/537.36'
    }
    res = requests.get(url=url, headers=headers)

    return res.text

def get_pages_count(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    pages_count = soup.find(
        'div', class_='pagination-numbers__right').find_all('a')[-1].text

    return pages_count

def get_data(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')

    books = soup.find('tbody', class_='products-table__body').find_all('tr')
    data_list = []
    for book in books:
        characteristics = book.find_all('td')
        try:
            book_name = characteristics[0].text.strip()
        except:
            print('Нет названия книги')
            book_name = ''
        try:
            book_author = characteristics[1].text.strip()
        except:
            print('Нет имени автора')
            book_author = ''
        try:
            book_ph = ' '.join([
                item.text for item in characteristics[2].find_all('a')
            ]).strip()
        except:
            print('Нет издательства книги')
            book_ph = ''
        try:
            book_new_price = int(characteristics[3].find(
                'span',
                class_='price-val').find('span').text.strip().replace(' ', ''))
        except:
            print('Нет новой цены книги')
            book_new_price = ''
        try:
            book_old_price = int(characteristics[3].find(
                'span', class_='price-gray').text.strip().replace(' ', ''))
        except:
            print('Нет старой цены книги')
            book_old_price = ''
        try:
            book_discount = str(
                round((book_old_price - book_new_price) / book_old_price * 100)) + '%'
        except:
            print('Нет скидки')
            book_discount = ''
        try:
            book_existence = characteristics[5].text.strip()
        except:
            print('Нет в наличии')
            book_existence = ''
            
        data = {
            'book_name': book_name,
            'book_author': book_author,
            'book_ph': book_ph,
            'book_new_price': book_new_price,
            'book_old_price': book_old_price,
            'book_discount': book_discount,
            'book_existence': book_existence
        }
        
        data_list.append(data)
        
        with open(f'{current_time}.csv', 'a', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow((
                book_name,
                book_author,
                book_ph,
                book_new_price,
                book_old_price,
                book_discount,
                book_existence
            ))
        
    return data_list

def make_json(json_data):
    with open('data.json', 'a', encoding='utf-8') as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)

def main():
    start_time = time.time()
    url = 'https://www.labirint.ru/genres/2308/?available=1&paperbooks=1&display=table&page=1&histlab=1946617022'
    
    with open(f'{current_time}.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow((
            'Название книги',
            'Автор',
            "Издательство",
            "Цена со скидкой",
            "Цена без скидки",
            "Процент скидки",
            "Наличие на складе"
        ))

    json_data = []
    pages_count = int(get_pages_count(url))

    for i in range(1, pages_count + 1):
        url = f'https://www.labirint.ru/genres/2308/?available=1&paperbooks=1&display=table&page={i}&histlab=1946617022'
        data_list = get_data(url)
        for data in data_list:
            json_data.append(data)
        print(f'[PROGRESS] {i}/{pages_count}')
        time.sleep(1.2)
        
    make_json(json_data)
    print(f'Время выполнения: {time.time() - start_time}')

if __name__ == '__main__':
    main()