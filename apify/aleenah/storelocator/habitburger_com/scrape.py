import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from bs4 import BeautifulSoup

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
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


def parse_geo(url):
    lon = re.findall(r'll=[-?\d\.]*\,([-?\d\.]*)', url)[0]
    lat = re.findall(r'll=(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    countries=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    page_url=[""]
    types=[]

    driver.get("https://www.habitburger.com/locations/all/")
    uls = driver.find_elements_by_class_name("reglist")
    del uls[-1] #china
    for ul in uls:
        ast=ul.find_elements_by_tag_name('a')
        for div in ast:
            l = div.get_attribute("href")
            if "/locations/" in l:
                if page_url[-1]!= l:
                    page_url.append(l)
    del page_url[0]
    print(len(page_url))
    coming_soon=[]
    for url in page_url:
        print(url)
        driver.get(url)
        cs=driver.find_elements_by_id("coming_soon")
        if cs != []:
            coming_soon.append(url)
            continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        scripts=soup.find_all("script")
        the_script= soup.find_all('script', {'type': 'application/ld+json'})[1]
        ind = scripts.index(the_script)

        tex = the_script.text
        #print(tex)
        locs.append(re.findall(r'.*"name": "([^"]*)"', tex)[0])
        types.append(re.findall(r'.*"@type": "([^"]*)"', tex)[0])
        c=re.findall(r'.*"addressLocality": "([^"]*)"', tex)[0]
        cities.append(c)
        s= re.findall(r'.*"addressRegion": "([^"]*)"', tex)[0]
        states.append(s)
        z=re.findall(r'.*"postalCode": "([^"]*)"', tex)[0]
        zips.append(z)
        street.append(re.findall(r'.*"streetAddress": "([^"]*)"', tex)[0].replace(z,"").replace(s,"").replace(c,"").strip())
        try:
            t=re.findall(r'.*"openingHours": \[.*"([^"]*)".*\],', tex, re.DOTALL)[0]
            if "<br>" in t:
                t=t.replace("<br>"," ")
            if "> " in t:
                t=t.replace("> ","")
            timing.append(t)
        except:
            timing.append("<MISSING>")
        try:
            phones.append(re.findall(r'.*"telephone": "([^"]*)"', tex)[0])
        except:
            phones.append("<MISSING>")
        tex = scripts[ind-1].text
        lat.append(re.findall(r'lat: (-?[\d\.]*),',tex)[0])
        long.append(re.findall(r'lng: (-?[\d\.]*)',tex)[0])

    for u in coming_soon:
        del page_url[page_url.index(u)]

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.habitburger.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
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