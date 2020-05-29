import csv
from sgselenium import SgSelenium
import re


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
    lon = re.findall(r'destination=[-?\d\.]*\,([-?\d\.]*)', url)[0]
    lat = re.findall(r'destination=(-?[\d\.]*)', url)[0]
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
    types=[]



    links = ["https://www.mystricklands.com/akron-ellet", "https://www.mystricklands.com/akron-montrose",
             "https://www.mystricklands.com/streetsboro-1", "https://www.mystricklands.com/cuyahoga-falls-1",
             "https://www.mystricklands.com/green"]

    for link in links:
        driver.get(link)

        div = driver.find_element_by_xpath('//div[@class="p1inlineContent"]')
        locs.append(div.find_element_by_tag_name("h2").text)
        #div = div.find_element_by_class_name("txtNew")
        tex = div.text
        for i in ["Click Here for Flavors of the Day","Follow us on Facebook!","Click Here for our Menu","We are open year-round! ","Click Here For Flavors of the Day","Open Year Round with Indoor Seating!","Follow us on Facebook!","OPEN 7 DAYS A WEEK!","Voted #1 Beacon's Best and Fox 8 Hot List !","Our Stricklands Gift Cards make the perfect gift for any occasion!","Flavor of the Day"]:
            if i in tex:
                tex=tex.replace(i,"").strip()
        timing.append(re.findall(r'(Hours.*pm|Hours.*PM)',tex,re.DOTALL)[0].replace("\n"," "))
        #tex.replace(tim,"")
        phones.append(re.findall(r'Phone:*([0-9\-\(\) ]+).*',tex,re.DOTALL)[0].strip())


        tex=tex.split("\n")

        for te in tex:
            z= re.findall(r'([0-9]{5})',te)
            if z !=[]:
                zips.append(z[0])
                t=te.split(",")
                c=t[0].strip().split(" ")
                if len(c) >2:
                    cities.append(c[-1])
                    s=t[0].replace(c[-1],"").strip()
                    if "(" in s:
                        s=tex[tex.index(te)-1].strip()+s
                    street.append(s)
                else:
                    cities.append(t[0])
                    s=tex[tex.index(te)-1].strip()
                    if "(" in s:
                        s=tex[tex.index(te)-2].strip()+s
                    street.append(s)
                states.append(t[1].strip().split(" ")[0])
        print(street)


    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.mystricklands.com")
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
        row.append(links[i])  # page url

        all.append(row)
    return (all)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

