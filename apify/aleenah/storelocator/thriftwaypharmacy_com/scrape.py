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
    lon = re.findall(r'll=[-?\d\.]*\,([-?\d\.]*)', url)[0]
    lat = re.findall(r'll=(-?[\d\.]*)', url)[0]
    return lat, lon

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

    driver.get("http://www.thriftwaypharmacy.com/store_locations.html")
    div=driver.find_element_by_xpath("/html/body/table[2]/tbody/tr[2]/td[1]/table/tbody/tr[2]/td")
    ps=div.find_elements_by_tag_name("p")
    i=0
    for p in ps:
        tex=p.text
        if tex == " " or len(tex.split(" "))==1:
            continue

        loc = tex.split("\n")[0]
        locs.append(loc)
        if i==0:
            tex=tex.replace(loc,"")

        addr=re.findall(r'(.* [0-9]{5}).*',tex,re.DOTALL)[0].replace("\n"," ")
        tex=tex.replace(addr,"")
        z=re.findall(r'([0-9]{5})',addr)[-1]
        addr=addr.replace(z,"")
        zips.append(z)
        s = re.findall(r'([A-Z]\.*[A-Z]\.*)',addr)[0]
        addr=addr.replace(s,"")
        s=s.replace(".","")
        states.append(s)
        addr= addr.strip().strip(",")
        if "New York" in addr:
            c= "New York"
        else:
            c=addr.split(" ")[-1]
        addr=addr.replace(c,"")
        cities.append(c)
        street.append(addr.strip().strip(","))

        p = re.findall(r'Tel ([0-9 \-\(\)]+) \- Fax',tex)
        if p ==[]:
            p = re.findall(r'Phone: ([0-9 \-\(\)]+) \- Fax', tex)
        p=p[0]
        phones.append(p)

        tim = re.findall(r'Monday.*Sunday',tex,re.DOTALL)
        if tim == []:
            tim = re.findall(r'Monday.*pm', tex, re.DOTALL)
            if tim==[]:
                tim="<MISSING>"
            else:
                tim=tim[0].replace("\n"," ")
        else:
            tim=tim[0].replace("\n"," ")
        timing.append(tim)
        types.append("<MISSING>")

        if i ==1:
            locs.append(loc)
            zips.append(z)
            street.append(addr)
            cities.append(c)
            states.append(s)
            phones.append(p)
            timing.append(tim)
            types.append("<MISSING>")
        i += 1
    trs = driver.find_element_by_xpath("/html/body/table[2]/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/table").find_elements_by_tag_name("tr")
    i=0
    tim1=""
    tim2=""
    for tr in trs:
        ps=tr.find_elements_by_tag_name("p")
        if i==0:
            types[1]=ps[1].text
            types[2]=ps[2].text
            i+=1
            continue

        tim1+=(ps[0].text+" "+ps[1].text+" ")
        tim2+=(ps[0].text+" "+ps[2].text+" ")
    timing[1]=tim1
    timing[2]=tim2

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("http://www.thriftwaypharmacy.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append(types[i])  # type
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append(timing[i])
        row.append("http://www.thriftwaypharmacy.com/store_locations.html")

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

fetch_data()
