from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import re
import os
import csv


def save_index_page():
    useragent = UserAgent()
    headers = {
        'User-Agent': f'{useragent.random}',
        'Content-Type': 'text/html; charset=utf-8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
                  ',application/signed-exchange;v=b3;q=0.7'
    }
    url = 'https://www.contractresearchmap.com/'

    response = requests.get(url=url, headers=headers)
    html = response.text
    if os.path.exists('data') is not True:
        os.mkdir('data')

    with open('data/index.html', 'w', encoding='utf-8') as file:
        file.write(html)


def create_country_links():
    '''
    'https://contractresearchmap.com/places/united-states'
    :return: Links to the countries where the companies are located
    '''
    with open('data/index.html') as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')

    find_title_country = soup.find_all(class_='item__title')
    title_country = []

    for country in find_title_country:
        title_country.append(country.text.lower().replace(' ', '-'))

    country_links = []
    domain = r'https://contractresearchmap.com/places/'

    for country in title_country:
        country_links.append(domain + country.replace('.', ''))

    return country_links


def create_city_links(url):
    useragent = UserAgent()
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent = {useragent.random}')
    options.add_argument("--disable-infobars")
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(
        executable_path=r'C:\Users\kcern\PycharmProjects\request\contractresearchmap\chromedriver.exe',
        options=options
    )

    city_links_all = []

    try:
        driver.get(url)
        time.sleep(5)
        city_urls = driver.find_elements(By.CLASS_NAME, 'item__link')

        for link in city_urls:
            city_links_all.append(link.get_attribute('href'))
            print(f"[Link has been added]: {link.get_attribute('href')}")

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

    name_file = url[39:].replace('-', '_').upper()

    if os.path.exists('csv_file') is not True:
        os.mkdir('csv_file')

    with open(f'csv_file/{name_file}.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(
            [
                'Year Established',
                'Website',
                'Headquarters',
                'Company Type',
                'Description'
            ]
        )

    for link in city_links_all:
        headers = {
            'User-Agent': f'{useragent.random}'
        }

        response = requests.get(url=link, headers=headers)

        soup = BeautifulSoup(response.text, 'lxml')

        try:
            year_established = soup.find('small', text='Year Established:').find_previous().text.strip()[-4:]
            year_established = re.sub("^\s+|\n|\r|\s+$", '', year_established)
        except AttributeError:
            year_established = 'None'

        try:
            website = soup.find('a', class_='trackable').get('href')
            website = re.sub("^\s+|\n|\r|\s+$", '', website)
        except AttributeError:
            website = 'None'

        try:
            headquarters = soup.find('small', text='Headquarters:').find_previous().text.strip()[13:]
            headquarters = re.sub("^\s+|\n|\r|\s+$", '', headquarters)
        except AttributeError:
            headquarters = 'None'

        try:
            company_type = soup.find('small', text='Company Type:').find_previous().text.strip()[13:]
            company_type = re.sub("^\s+|\n|\r|\s+$", '', company_type)
        except AttributeError:
            company_type = 'None'

        try:
            description = soup.find('div', class_='tab-pane active').find('p').text
            description = re.sub("^\s+|\n|\r|\s+$", '', description)
        except AttributeError:
            description = 'None'

        with open(f'csv_file/{name_file}.csv', 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(
                [
                    year_established,
                    website,
                    headquarters,
                    company_type,
                    description
                ]
            )

        print(f'[+]: {name_file}.csv data has been added from {link}')


if __name__ == '__main__':
    urls = create_country_links()

    for url in urls[1:10]:
        create_city_links(url)
