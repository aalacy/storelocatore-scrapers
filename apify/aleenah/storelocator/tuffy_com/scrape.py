import csv
from sgselenium import SgSelenium
import re
from pyzipcode import ZipCodeDatabase
import time

driver = SgSelenium().chrome()

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
    page_url=[]
    US_states=["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New+Hampshire","New+Jersey","New+Mexico","New+York","North+Carolina","North+Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode+Island","South+Carolina","South+Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West+Virginia","Wisconsin","Wyoming"]

    for us in US_states:
        url="https://www.tuffy.com/location_search?zip_code="+us

        driver.get(url)
        inp=driver.find_element_by_xpath('/html/body/div[3]/main/section[1]/div/form/fieldset/input')
        inp.click()
        time.sleep(5)

        try:
            divs=driver.find_element_by_xpath('//div[@class="col contact-info-hlder"]')
            divs=divs.find_elements_by_class_name("contact-info")
            for div in divs:

                loc=div.find_element_by_tag_name("h2").get_attribute("innerText")
                loc=re.sub(r'\d+',"",loc).strip()

                if loc in locs:
                    continue
                locs.append(loc)

                addr=div.find_element_by_tag_name("address").get_attribute("innerText")

                #addr=add.text
                p=div.find_element_by_class_name("tel").get_attribute("innerText")
                tim=div.find_element_by_class_name("schedule-holder").get_attribute("innerText")
                if p!="":
                    phones.append(p.strip())
                else:
                    phones.append("<MISSING>")
                if tim!="":
                    timing.append(tim.replace("\n"," ").strip().replace("  "," "))
                else:
                    timing.append("<MISSING>")

                addr=addr.split("\n")[0]
                addr=addr.split(",")
                sz=addr[-1].strip().split(" ")
                states.append(sz[0])
                z=sz[1]
                addr=addr[0].strip(",")
                zips.append(z)
                zcdb = ZipCodeDatabase()
                z=zcdb[int(re.findall(r'[0-9]{5}',z)[0])]
                c= z.place
                if c in addr:
                    addr=addr.replace(c,"").strip()
                    cities.append(c)
                    street.append(addr)
                else:
                    c=addr.strip().split(" ")[-1]
                    cities.append(c)
                    street.append(addr.replace(c,"").strip())
                lat.append(z.latitude)
                long.append(z.longitude)
                page_url.append(url)

        except:
           continue

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.tuffy.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page_url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
