import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
#import reverse_geocoder
#from slimit.parser import Parser


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
    links=[]

    driver.get("https://www.spiritofmath.com/campuses/")

    uls = driver.find_elements_by_class_name("list-unstyled")
    for i in range(37):
        li = uls[i]
        tex=li.text.split("\n")

        addr=tex[1]

        if "Pakistan" in addr:
            continue

        e = re.findall(r'( [ABCEGHJ-NPRSTVXY][0-9][ABCEGHJ-NPRSTV-Z] [0-9][ABCEGHJ-NPRSTV-Z][0-9])', addr) #canadian zip
        if e != []:
            addr = addr.replace(e[0], "")
            zips.append(e[0].strip())
            countries.append("CA")
        else:
            e = re.findall(r'( [0-9]{5})', addr) #american zip
            if e != []:
                addr = addr.replace(e[0], "")
                zips.append(e[0].strip())
                countries.append("US")
            else:
                zips.append("<MISSING>")
                countries.append("<MISSING>")

        e = re.findall(r'.*( [A-Z]{2}[ \,]*)$', addr)
        if e != []:
            addr = addr.replace(e[0], "")
            states.append( e[0].strip().strip(","))
        else:
            e = re.findall(r'.*( Ontario[ \,]*)$', addr)
            if e != []:
                addr = addr.replace(e[0], "")
                states.append(e[0].strip().strip(","))
            else:
                states.append("<MISSING>")
        addr=addr.strip().strip(",")
        o =addr.split(",")[-1].strip()
        addr=addr.replace(o,"").strip().strip(",")
        cities.append(o)
        street.append(addr)
        locs.append(tex[0])
        e=re.findall(r'([0-9\-]+.*)', tex[2].strip())
        if e != []:
            phones.append(e[0].replace("MATH ",""))
        else:
            phones.append("<MISSING>")
        links.append(li.find_element_by_tag_name("a").get_attribute("href"))
    """ to extract lat long and country
    for link in links:
        driver.get(link)
        div=driver.find_element_by_class_name("popup-holder")
        scripts= div.find_elements_by_css_selector("script")
        parser=Parser()
        tex=""
        for s in scripts:
            tex+=s.text
        print(tex)
        la= re.findall(r'var myLatLng = {lat: (.*),',tex)[0]
        lat.append(la)
        lo= re.findall(r'var myLatLng = {lat: .* lng: (.*)}',tex)[0]
        long.append(lo)
        cord=(la,lo)
        countries.append(reverse_geocoder.search(cord)[0]["cc"])
    """



    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.spiritofmath.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append(countries[i])
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<INACCESSIBLE>")  # type
        row.append("<INACCESSIBLE>")  # lat
        row.append("<INACCESSIBLE>")  # long
        row.append("<INACCESSIBLE>")

        all.append(row)
    return all




def scrape():
    data = fetch_data()
    write_output(data)

scrape()