import csv
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36")
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]
    state_urls=[]
    city_urls=[]
    headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "en-US,en;q=0.9",
"Cache-Control": "max-age=0",
"Connection": "keep-alive",
            "Host": "www.cellularsales.com",
#Referer: https://www.cellularsales.com/store/home/
"Sec-Fetch-Mode": "navigate",
"Sec-Fetch-Site": "same-origin",
"Sec-Fetch-User": "?1",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}
    #res=requests.get("https://www.cellularsales.com/store/stores/",headers=headers)
    driver.get("https://www.cellularsales.com/store/stores/")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    #print(soup)
    sa = soup.find('ul', {'class': 'st-states-list'}).find_all('a')
    #print(soup)
    for a in sa:
        state_urls.append("https://www.cellularsales.com/"+a.get('href'))
    print("states: ", len(state_urls))
    for url in state_urls:
        driver.get(url)
        print(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        sa = soup.find('ul', {'class': 'st-states-list'}).find_all('a')

        for a in sa:
            city_urls.append("https://www.cellularsales.com/" + a.get('href'))

    print("cities: ",len(city_urls))
    for url in city_urls:
        print(url)
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
                sa = soup.find('ul', {'id': 'cityBox'}).find_all('a')
        except:
            page_url.append(u)
            print(url)
            #driver.get(u)
            #time.sleep(5)
            #soup = BeautifulSoup(driver.page_source, 'html.parser')
            locs.append("<MISSING>")
            ids.append("<MISSING>")
            cities.append("<MISSING>")
            street.append("<MISSING>")
            states.append("<MISSING>")
            zips.append("<MISSING>")
            phones.append("<MISSING>")
            timing.append("<MISSING>")
            continue
        for a in sa:
            u="https://www.cellularsales.com/" + a.get('href')
            page_url.append(u)
            #print(url)
            driver.get(u)
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            locs.append(soup.find('h1', {'itemprop': 'name'}).text)
            ids.append(soup.find('input', {'id': 'locationId'}).get('value'))
            cities.append(soup.find('span', {'itemprop': 'addressLocality'}).text)
            street.append(soup.find('span', {'itemprop': 'streetAddress'}).text)
            states.append(soup.find('span', {'itemprop': 'addressRegion'}).text)
            z=soup.find('span', {'itemprop': 'postalCode'}).text.strip()
            if len(z)>5:
                z=re.findall(r'[\d]{5}',z)[0]
            elif len(z)==4:
                z="0"+z
            zips.append(z)
            ph=soup.find('span', {'itemprop': 'telephone'}).text.strip()
            if ph=="":
                ph="<MISSING>"
            phones.append(ph)
            tim= soup.find('div',{'id':'special_hour'}).text.strip().replace("\n"," ")
            if tim=="":
                tim="<MISSING>"
            timing.append(tim)


    print("stores: ", len(page_url))

    all = []
    for i in range(0, len(locs)):
        row = []
        if locs[i]=="<MISSING>":
            continue
        row.append("https://www.cellularsales.com/")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
