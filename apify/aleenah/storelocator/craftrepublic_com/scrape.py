import csv
import re
from bs4 import BeautifulSoup
import requests
from sgselenium import SgSelenium


driver = SgSelenium().chrome()

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

    res=requests.get("https://www.craftrepublic.com/locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find_all('a', {'class': 'locationLink'})
    for div in divs:
        page_url.append("https://www.craftrepublic.com"+div.get('href'))
    """header={"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"accept-encoding": "gzip, deflate, br",
"accept-language": "en-US,en;q=0.9",
"cache-control": "max-age=0",
"sec-fetch-mode": "navigate",
"sec-fetch-site": "none",
"sec-fetch-user": "?1",
"upgrade-insecure-requests": "1",
"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"}"""
    for url in page_url:
        print(url)
        driver.get(url)
        #res=requests.get(url,headers=header)
        #print(res)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        #ids.append(soup.find('div', {'class': 'mfcard'}).get('location_id'))
        locs.append(soup.find('h3', {'itemprop': 'name'}).text)
        states.append(soup.find('span', {'itemprop': 'addressRegion'}).text)
        c=soup.find('span', {'itemprop': 'addressLocality'}).text
        cities.append(c)
        zips.append(soup.find('span', {'itemprop': 'postalCode'}).text)
        addr=re.sub(r"[ ]+",r" ",soup.find('h4', {'itemprop': 'streetAddress'}).text.split(c)[0].strip()).strip(",").strip().replace("\n","")
        #print("**"+addr+"**")
        street.append(addr)
        phones.append(soup.find('span', {'itemprop': 'telephone'}).text)
        lat.append(soup.find('meta', {'itemprop': 'latitude'}).get('content'))
        long.append(soup.find('meta', {'itemprop': 'longitude'}).get('content'))
        #types.append(soup.find('meta', {'property': 'og:type'}).get('content'))
        hr=soup.find('dl', {'itemprop': 'openingHours'})

        dts=hr.find_all('dt')
        dds=hr.find_all('dd')
        print(len(dts),len(dds))
        tim=""
        for i in range(0,7):
            tim+= dts[i].text.strip()+" "+dds[i].text.strip()+" "
        timing.append(tim.strip())
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.craftrepublic.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append( "<MISSING>")  # type
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
