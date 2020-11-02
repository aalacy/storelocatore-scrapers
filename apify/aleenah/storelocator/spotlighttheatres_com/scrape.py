import csv
from sgselenium import SgSelenium
import re

driver = SgSelenium().chrome()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
    urls=[]

    driver.get("http://www.spotlighttheatres.com")
    ast= driver.find_elements_by_tag_name("a")
    #ast=ast.find_elements_by_class_name("btn btn-default")
    for a in ast:
        if a.get_attribute("class")=="btn btn-default":
            urls.append(a.get_attribute("href"))

    for url in urls:
        driver.get(url)
        addr=driver.find_element_by_tag_name("address").text
        addr=addr.split("\n")
        locs.append(addr[0])
        street.append(addr[1])
        phones.append(re.findall(r'([0-9\-]+.*)',addr[3])[0])
        addr=addr[2].split(",")
        cities.append(addr[0])
        addr=addr[1].strip().split(" ")
        states.append(addr[0])
        zips.append(addr[1])
        """
        driver.get(url+"/map")
        
        driver.find_element_by_id("map-container")
        ast=driver.find_elements_by_tag_name("a")
        for a in ast:
            if a.get_attribute("title")=="Open this area in Google Maps (opens a new window)":
                la,lo = parse_geo(a.get_attribute("href"))
                lat.append(la)
                long.append(lo)
        """
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("www.spotlighttheatres.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append("<INACCESSIBLE>")  # lat
        row.append("<INACCESSIBLE>")  # long
        row.append("<MISSING>") #timing

        all.append(row)
    return (all)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
