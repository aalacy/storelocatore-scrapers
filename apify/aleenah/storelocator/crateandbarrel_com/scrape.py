import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from bs4 import BeautifulSoup
import time


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def scroll():
    height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == height:
            break
        height = new_height


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
    countries = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]
    state_url=[]
    urls=["https://www.crateandbarrel.com/stores/list-province/canada-stores","https://www.crateandbarrel.com/stores/list-state/retail-stores"]

    for url in urls:
        driver = webdriver.Chrome(executable_path='chromedriver.exe')
        driver.implicitly_wait(10)
        driver.get(url)
        scroll()
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()

        div = soup.find('div',{'class':'state-list'})
        sa= div.find_all("a")
        for a in sa:
            state_url.append(a.get("href"))

    for url in state_url:
        url = "https://www.crateandbarrel.com"+url
        driver = webdriver.Chrome(executable_path='chromedriver.exe')
        driver.implicitly_wait(10)
        driver.get(url)
        scroll()
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print(soup)
        #driver.close()
        print(driver.execute_script("return Crate.Model.StoreList") )
        div = driver.find_element_by_class_name('main-body-container')
        scripts = div.find_element_by_xpath("//script[@type='application/ld+json']")
        #scripts = re.findall(r'<script type="application/ld\+json">(.*)</script>',str(soup))
        print(len(scripts))
        del scripts[-1]
        del scripts[-1]
        del scripts[-1]

        for script in scripts:
            tex=script.text
            types.append(re.findall(r'.*"@type":"([^"]*)"', tex)[0])
            locs.append(re.findall(r'.*"name":"([^"]*)"', tex)[0])
            phones.append(re.findall(r'.*"telephone":"([^"]*)"', tex)[0])
            timing.append(re.findall(r'.*"openingHours":\["(.*)"\],', tex)[0])
            cities.append(re.findall(r'.*"addressLocality":"([^"]*)"', tex)[0])
            states.append(re.findall(r'.*"addressRegion":"([^"]*)"', tex)[0])
            zips.append(re.findall(r'.*"postalCode":"([^"]*)"', tex)[0])
            street.append(re.findall(r'.*"streetAddress":"([^"]*)"', tex,re.DOTALL)[0].replace("\n"," "))
            lat.append(re.findall(r'.*"latitude":(-?[\d\.]*)', tex)[0])
            long.append(re.findall(r'.*"longitude":(-?[\d\.]*)', tex)[0])
            if "canada" in url:
                countries.append("CA")
            else:
                countries.append("US")
            page_url.append(url)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.crateandbarrel.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append(countries[i])
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append(types[i])  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()