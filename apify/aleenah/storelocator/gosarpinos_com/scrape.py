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

    driver.get("https://www.gosarpinos.com")
    driver.find_element_by_class_name("location-link__caption").click()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    #print(soup)
    lis = soup.find('select', {'class': 'select2 select2_restaurant form-control select2-hidden-accessible'}).find_all("option")
    del lis[0]
    print(len(lis))
    for li in lis:

        ids.append(li.get("value"))
        tex= li.text.split("-")
        #print(tex)
        states.append(tex[0].strip())
        t=tex[0]+"- "

        l=li.text.replace(t,"")

        locs.append(l)
        if "Lee's" in l:
            l=l.replace("Lee's","lee-s")

        page_url.append("https://www.gosarpinos.com/pizza-delivery/"+l.replace("'","").replace("& ","").replace(" - ","-").replace("- ","-").replace(" ","-"))

    for url in page_url:
        print(url)
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        script = soup.find_all("script")[-1].text.split('"intId"')
        days = re.findall(r'"day":"([^"]+)"', script[0])
        shed = re.findall(r'"workingHours":"([^"]+)"', script[0])
        tim = ""

        for i in range(7):
            tim += days[i] + " " + shed[i] + " "

        timing.append(tim)
        script=script[1]
        street.append(re.findall(r'"address":"([^"]+),"',script)[0])
        cities.append(re.findall(r'"city":"([^"]+)"',script)[0])
        zips.append(re.findall(r'"postalCode":"([^"]+)"',script)[0])
        phones.append(re.findall(r'"phone":"([^"]+)"',script)[0])
        lat.append(re.findall(r'"latitude":(-?[\d\.]*)',script)[0])
        long.append(re.findall(r'"longitude":(-?[\d\.]*)',script)[0])

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.gosarpinos.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
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