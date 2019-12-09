from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv
import re
import requests
import pandas as pd
import time


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def write_output(df):
    df.to_csv('nl.csv', index=False)


def get_driver():
    options = Options()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome("C:/Users/Latika Bisht/PycharmProjects/chromedriver.exe", options=options)
    # driver = webdriver.Chrome("chromedriver", options=options)


driver1 = get_driver()

data_list = []
cities = []
states = []
hours = []
zip_codes = []
phones = []
street_address = []
lats = []
longts = []
location_names = []
locator_domains = []
page_urls = []
country_codes = []
store_numbrs = []
location_types = []
pattern = re.compile(r'\s+')


def fetch_data():
    try:
        base = 'https://www.lesliespool.com/'
        urls = 'https://www.lesliespool.com/directory/stores.htm'
        html = requests.get(urls).text
        soup = BeautifulSoup(html)
        content = soup.find("div", id="mainContainer")
        new_lis = content.find('table').findAll('td', style="padding-left: 35px;")

        for j in new_lis:
            loc = j.find('a')
            url = (base + loc.get('href'))
            try:
                response = requests.get(url, timeout=6)
            except Exception as e:
                continue
            if response.status_code == 200:
                page_url = url
                page_urls.append(page_url)
                res = response
                response.close()
                data = res.text
                soup = BeautifulSoup(data, 'html.parser')

                np = re.compile(r'\s+\-')
                try:
                    c = soup.find('div', class_="name").text.strip()
                    ct = re.sub(np, " ", c)
                    city = ct.split('#')[0]
                except Exception as e:
                    city = "<MISSING>"
                print(city)
                cities.append(city)

                try:
                    st = soup.find('h1', class_="top_heading").text.strip()
                    state = st.split(',')[-1].strip()
                except Exception as e:
                    state = "<MISSING>"
                print(state)
                states.append(state)

                try:
                    strt = soup.find('div', class_="location").contents
                    street = strt[0]
                except Exception as e:
                    street = "<MISSING>"
                print(street)
                street_address.append(street)

                try:
                    store = soup.find('div', class_="location").contents[2]
                    strn = store.split('-')[1]
                    strnum = re.findall(r"\d{3,}", strn)
                    store_numbr = strnum[0]

                    if len(store_numbr) < 3:
                        store_numbr = '<MISSING>'
                except Exception as e:
                    store_numbr = "<MISSING>"

                store_numbrs.append(store_numbr)

                try:
                    store = soup.find('div', class_="location").contents[2]
                    zp = store.split('-')[0]
                    zp_code = re.findall(r"\d{5}", zp)
                    zip_code = zp_code[0]

                    if len(zip_code) < 3:
                        zip_code = '<MISSING>'

                except Exception as e:
                    zip_code = "<MISSING>"
                zip_codes.append(zip_code)
                print(zip_code)

                try:
                    for i in soup.find('div', class_='store_page').findAll('div', class_='phone'):
                        phn = i.text
                    if len(phn) < 3:
                        phn = '<MISSING>'

                except Exception as e:
                    phn = "<MISSING>"
                phones.append(phn)
                print(phn)

                result = soup.findAll('div', class_='hours_col')
                hour = ''
                try:
                    for i in result:
                        n = i.findAll('span', class_='store_day')
                        m = i.findAll('span', class_='store_hours')
                        for i in m:
                            l = i.text
                            pat = re.sub(pattern, "", l)
                        for i in n:
                            b = i.text.strip()
                            pat1 = re.sub(pattern, "", b)

                            hoo = pat1 + ' ' + pat + ' ' + '|'
                            hour = hour + hoo + ' '
                    if len(hour) < 3:
                        hour = "<MISSING>"

                except Exception as e:
                    hour = "<MISSING>"
                print(hour)
                hours.append(hour)

                try:
                    lc = soup.find('h1', class_="top_heading")
                    location_name = lc.text.strip()

                except Exception as e:
                    location_name = "<MISSING>"

                location_names.append(location_name)

                country_code = "US"
                country_codes.append(country_code)

                location_type = "<MISSING>"
                location_types.append(location_type)

                locator_domain = "https://www.lesliespool.com"
                locator_domains.append(locator_domain)

                new_list = [page_url]
                try:
                    for i in new_list:
                        driver1.get(i)
                        time.sleep(6)
                        stores = driver1.find_element_by_xpath('//*[@id="map-canvas"]/div/div/div[7]/div[2]/a').get_attribute("href")
                        st = stores
                        try:
                            lat, lon = parse_geo(st)
                        except Exception as e:
                            lat = "<MISSING>"
                            lon = "<MISSING>"

                except Exception as e:
                    lat = "<MISSING>"
                    lon = "<MISSING>"

                print(lat)
                lats.append(lat)
                print(lon)
                longts.append(lon)

        dic = {'locator_domain': locator_domains, 'page_url': page_urls, 'location_name': location_names,
               'street_address': street_address, 'city': cities, 'state': states,
               'zip': zip_codes, 'country_code': country_codes, 'phone': phones, 'location_type': location_types,
               'latitude': lats, 'longitude': longts, 'hours_of_operation': hours, 'store_number': store_numbrs}
        d = pd.DataFrame(dic)
        df = d.drop_duplicates()
        driver1.quit()
        return df


    except Exception as e:
        print(str(e))


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
