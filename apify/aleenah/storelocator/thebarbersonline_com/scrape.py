import csv
from sgselenium import SgSelenium
import re
from bs4 import BeautifulSoup
from pyzipcode import ZipCodeDatabase

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

    driver.get("https://thebarbersonline.com/locations/")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pag=soup.find_all('a',{'class':'locgrid__link'})
    for pa in pag:
        page_url.append(pa.get('href'))

    names=soup.find_all('h4',{'class':'locgrid__name'})
    for nam in names:
        locs.append(nam.text)

    for url in page_url:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        divs = soup.find_all('div', {'class': 'submaphours__item submaphours_item--span3'})
        p=re.findall(r'([0-9 \(\)\-\.]+)',divs[0].text)
        if p ==[]:
            phones.append("<MISSING>")
        else:
            phones.append(p[0].strip())

        addr= divs[1].text.replace('Location',"").strip()
        addr = addr.split(",")
        ad=addr[-1].strip().split(" ")
        states.append(ad[0])
        z=re.findall(r'[0-9]{5}',ad[1])[0]
        zips.append(z)
        zcdb = ZipCodeDatabase()
        c = zcdb[z].place
        if c in addr[-2]:
            cities.append(c)
            addr[-2] = addr[-2].replace(c, "")
        else:
            c=addr[-2].split(" ")[-1]
            cities.append(c)
            addr[-2] = addr[-2].replace(c, "")
        del addr[-1]
        st=""
        for sa in addr:
            st+=sa

        street.append(st)

        t= divs[2].text.replace("Hours","").strip()
        if t =="":
            timing.append("<MISSING>")
        else:
            timing.append(t)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://thebarbersonline.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
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