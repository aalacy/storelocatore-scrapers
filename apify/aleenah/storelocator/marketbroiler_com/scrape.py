import requests
import re

from bs4 import BeautifulSoup
import csv

def parse_geo(url):
    lon = re.findall(r' ll=[-?\d\.]*\,([-?\d\.]*)', url)[0]
    lat = re.findall(r'll=(-?[\d\.]*) ', url)[0]
    return lat, lon

def write_output(data):
    with open('data.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

        file.close()

def fetch_data():
    url = "https://www.marketbroiler.com"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    info = soup.find_all('div', {'id': 'comp-inhlqtpd'})

    div_ids=["comp-jf4l8jr4","comp-jf4hz517","comp-jf4h8s4l","comp-jf4jac7l1","comp-jf4ho1if1"]

    locations = re.search(r"<span class=\"color_12\">(.*)</span></span></span>", str(info))  # extract locations
    locs = locations.group(1).split(",")

    del (locs[3])
    for loc in locs:
        locs[locs.index(loc)] = loc.lower().replace(" ", "")
    print(locs)

    pix = ["17", "17", "20", "23", "20"]
    street = []
    cities = []
    states = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []

    for loc in locs:
        url="https://www.marketbroiler.com/"+loc
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        spans = soup.find_all('span', {'style':'font-size:'+pix[locs.index(loc)]+"px;"})
        data=[]
        for span in spans:
            t= span.text
            if"(" in t:
                continue
            else:
                data.append(t)
        street.append(data[0])
        cities.append(data[1].split(",")[0])
        sz= data[1].split(",")[1]
        sz = sz.split(" ")
        if "" in sz:
            del sz[sz.index("")]
        states.append(sz[0])
        zips.append(sz[1])
        if len(data) >2:
            phones.append(data[2])
        else:
            phones.append("<INACCESSIBLE>")

        clas = soup.find_all('div', {'id':div_ids[locs.index(loc)]})
        tim=re.findall(r'<p class="font_8">(.*)</p>.*',str(clas))
        st=""
        for h in tim:
            st+=(" "+h)
        timing.append(st)
        print (tim)

        #geomap = soup.find_element_by_css_selector('div.google-maps-link > a').get_attribute('href')
        #lat, lon = parse_geo(geomap)
        #print ("lat ",lat," long ",lon)
        #break

    all =[]
    for i in range (0,len(locs)):
            row=[]
            row.append("https://www.marketbroiler.com")
            row.append(locs[i])
            row.append(street[i])
            row.append(cities[i])
            row.append(states[i])
            row.append(zips[i])
            row.append("US")
            row.append("<MISSING>")                 #as not available on website
            row.append(phones[i])
            row.append("<MISSING>")
            row.append("<INACCESSIBLE>")
            row.append("<INACCESSIBLE>")
            row.append(timing[i])

            all.append(row)

    #the final location not accessible by code hence manually scraped
    row= ["https://www.marketbroiler.com", "mb-grille", "1161 Simi Town Center Way(118 and First Street)", "Simi Valley", "CA", "93065-0512", "US", "<MISSING>","(805) 210-7640", "<MISSING>", "<MISSING>", "<MISSING>", "MONDAY - THURSDAY 4PM - 10PM,FRIDAY  3PM - 10PM,SATURDAY & SUNDAY     12PM-10PM"]

    all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()