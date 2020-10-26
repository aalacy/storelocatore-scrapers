import time
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

    driver.get("https://shop.cleosfurniture.com/stores/store-info")
    info = driver.find_elements_by_xpath("//div[@class='wpb_text_column wpb_content_element ']")

    locs=[]
    street = []
    cities = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []

    del info[0]

    for a in info:
        data=a.text.split("\n")
        locs.append(data[0])

        street.append(data[1])
        phones.append(data[2])
        timing.append(data[4]+" "+data[5]+" "+data[6])
    for loc in locs:
        loc=loc.lower()
        print(loc)
        s = loc.split(" ")
        if len(s)==2:
            loc=s[0]+"-"+s[1]
        elif len(s)==3:
            loc = s[0] + "-" + s[1]+ "-" + s[2]
        elif len(s)==4:
            loc=s[0]+"-"+s[1]

        driver.get("https://shop.cleosfurniture.com/stores/"+loc)
        info = driver.find_elements_by_xpath("//div[@class='wpb_text_column wpb_content_element ']")

        data=info[0].text.split("\n")[4].split(",")
        cities.append(data[0])
        try:
            zips.append(data[1].split(" ")[2])
        except:
            zips.append("<MISSING>")
        """     to access location
        geomap = driver.find_elements_by_class_name('google-maps-link')
        print(str(info.text))
        link=""
        for a in geomap:
            print(a.get_attribute("href"))
            if "maps?ll=" in a.get_attribute("href"):
                link =a.get_attribute("href")

        #print(link)
        #lat, lon = parse_geo(str(geomap))
        #print(str(geomap))
        #link = driver.find_elements_by_xpath("//div[@class='google-maps-link']")
        #link2 = driver.find_element_by_css_selector('a').get_attribute('href')
        
        """
        time.sleep(1)

    all = []
    for i in range(0, len(locs)):
            row = []
            row.append("https://www.cleosfurniture.com")
            row.append(locs[i])
            row.append(street[i])
            row.append(cities[i])
            row.append("Arkansas")
            row.append(zips[i])
            row.append("US")
            row.append("<MISSING>")  # as not available on website
            row.append(phones[i])
            row.append("<MISSING>")
            row.append("<INACCESSIBLE>")
            row.append("<INACCESSIBLE>")
            row.append(timing[i])

            all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
