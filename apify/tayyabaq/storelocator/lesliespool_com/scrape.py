from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import csv
import requests
import time

def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon

def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        writer.writerows(data)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome("chromedriver", chrome_options=options)

driver1 = get_driver()

data_list = []
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
                res = response
                response.close()
                data = res.text
                soup = BeautifulSoup(data, 'html.parser')

                try:
                    c = soup.find('h1', class_="top_heading")
                    ct = c.text.split(',')
                    city = ct[0].split('-')[1].strip()

                except Exception as e:
                    city = "<MISSING>"

                try:
                    st = soup.find('h1', class_="top_heading").text.strip()
                    state = st.split(',')[-1].strip()
                except Exception as e:
                    state = "<MISSING>"

                try:
                    strt = soup.find('div', class_="location").contents
                    street_add = strt[0]
                    street = re.sub(r'(((?<=\s)|^|-)[a-z])', lambda x: x.group().upper(), street_add)

                except Exception as e:
                    street = "<MISSING>"

                try:
                    store = soup.find('div', class_="location").contents[2]
                    strn = store.split('-')[1]
                    strnum = re.findall(r"\d{3,}", strn)
                    store_numbr = strnum[0]

                    if len(store_numbr) < 3:
                        store_numbr = '<MISSING>'
                except Exception as e:
                    store_numbr = "<MISSING>"

                try:
                    store = soup.find('div', class_="location").contents[2]
                    zp = store.split('-')[0]
                    zp_code = re.findall(r"\d{5}", zp)
                    zip_code = zp_code[0]

                    if len(zip_code) < 3:
                        zip_code = '<MISSING>'

                except Exception as e:
                    zip_code = "<MISSING>"

                try:
                    for i in soup.find('div', class_='store_page').findAll('div', class_='phone'):
                        phn = i.text
                    if len(phn) < 3:
                        phn = '<MISSING>'

                except Exception as e:
                    phn = "<MISSING>"

                try:
                    result = soup.findAll('div', class_='hours_col')
                    h = []
                    for i in result:
                        n = i.findAll('span', class_='store_day')
                        m = i.findAll('span', class_='store_hours')
                        for i in m:
                            l = i.text
                            pat = re.sub(pattern, "", l)
                        for i in n:
                            b = i.text.strip()
                            pat1 = re.sub(pattern, "", b)

                            hoo = pat1 + ' ' + pat + ' '
                            h.append(hoo)

                        hour = ' '.join(h)
                    if len(hour) < 3:
                        hour = "<MISSING>"

                except Exception as e:
                    hour = "<MISSING>"
#                 print(hour)

                try:
                    lc = soup.find('h1', class_="top_heading")
                    l_name = lc.text.strip()
                    location_name = l_name.split(',')[0]

                except Exception as e:
                    location_name = "<MISSING>"

                country_code = "US"

                location_type = "<MISSING>"

                locator_domain = "https://www.lesliespool.com"

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

                n_list = [locator_domain, page_url, location_name, street, city, state, zip_code, country_code,
                            store_numbr, phn, location_type, lat, lon, hour]
                data_list.append(n_list)
        time.sleep(2)
        driver1.quit()
        return data_list

    except Exception as e:
        print(str(e))

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
