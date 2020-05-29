import csv
from sgselenium import SgSelenium
import re
from bs4 import BeautifulSoup

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
    ulinks=[]
    rlinks=[]
    #urls=["https://www.topman.com/store-locator?country=Canada","https://www.topman.com/store-locator?country=United+States"]
    driver.get("https://www.twistedtaco.com/locations#")
    #lis=driver.find_elements_by_css_selector("li ")

    ast=driver.find_element_by_id("1833213139").find_elements_by_tag_name("a")
    for a in ast:
        if a.text=='FULL SERVICE RESTAURANTS':
            continue
        if a.text=="Fayetteville":
            rlinks.append('https://www.twistedtaco.com/fayetteville-georgia')
            locs.append(a.text)
            continue
        elif a.text=='Suwanee':
            rlinks.append(a.get_attribute("href"))
            locs.append(a.text)
            break
        rlinks.append(a.get_attribute("href"))
        locs.append(a.text)

    ast = driver.find_element_by_id("1682398545").find_elements_by_tag_name("a")
    for a in ast:
        if a.text=="UNIVERSITY LOCATIONS":
            continue
        if"auburn"in a.get_attribute("href"):#coming soon
            continue
        ulinks.append(a.get_attribute("href"))
        locs.append(a.text)

    ast = driver.find_element_by_id("1253176376").find_elements_by_tag_name("a")
    for a in ast:
        ulinks.append(a.get_attribute("href"))
        locs.append(a.text)

    for link in rlinks:
        driver.get(link)

        try:
            div=driver.find_element_by_id("1315575225")
        except:
            div = driver.find_element_by_id("1876037087")
        data=div.text.split("\n\n")
        timing.append(data[0].replace("\n",""))
        data=data[1].split("\n")
        street.append(data[0])
        phones.append(data[2])
        s=re.findall(r'( [A-Za-z]{2})', data[1])[-1]
        z= re.findall(r'( [0-9]{5})', data[1])[0].strip()
        c = data[1].replace(z,"").replace(s,"").strip().strip(",")

        cities.append(c)
        states.append(s)
        zips.append(z)

    for link in ulinks:
        driver.get(link)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        a = soup.text
        #print(a)
        b = re.findall(r'(Monday.*)\*Hours are subject to change',a, re.DOTALL)[0]

        w=b.split(",")
        e = re.findall(r'( [0-9]{5})', w[-1])
        if e != []:
            b = b.replace(e[0], "")
            zips.append(e[0].strip(" ").strip(","))
        else:
            zips.append("<MISSING>")

        e = re.findall(r'( [A-Za-z]{2})', w[-1])
        if e != []:
            b = b.replace(e[0], "")
            states.append(e[0].strip(" ").strip(","))
        else:
            states.append("<MISSING>")

        b=b.rstrip('0123456789')
        c=b.strip(" ").split(" ")[-1]
        c= re.findall(r'([A-Z][a-z]+)',c)[-1]
        b=b.replace(c,"")
        cities.append(c.strip(","))

        mo = b.split(" ")
        mo=reversed(mo)
        g=""
        for w in mo:
            if "pm" in w:
                g=w.replace(re.findall(r"(.*pm)",w)[0],"")
                break
            elif "PM" in w:

                g = w.replace(re.findall(r"(.*PM)",w)[0], "")
                break
            elif "Closed" in w:

                g = w.replace(re.findall(r"(.*Closed)",w)[0], "")
                break
            elif "Midnight" in w:

                g = w.replace(re.findall(r"(.*Midnight)",w)[0], "")
                break

        t= re.findall('(Monday.*)'+g,b,re.DOTALL)[0]
        st=b.replace(t,"")

        if st!="":
            street.append(st)
        else:
            t=re.findall('(Monday.*pm)'+g,b,re.DOTALL)[0]
            st=b.replace(t,"")
            street.append(st)
        timing.append(t.replace("\n", ""))
        phones.append("<MISSING>")

    all = []
    for i in range(0, len(locs)):
        row=[]
        row.append("https://www.twistedtaco.com")

        row.append(locs[i])
        if street[i] != "":
            row.append(street[i])
        else:
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
        row.append(timing[i])

        all.append(row)
    return(all)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()