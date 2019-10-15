import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import usaddress
import json
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url" , "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    driver.get("https://mightyfineburgers.com/locations/")
    time.sleep(5)
    content = driver.page_source
    soup = BeautifulSoup(content)
    Address = []
    Loc_name = []
    Loc_name1 = []

    for a in soup.findAll(attrs={'class': 'accordion-container'}):
        name = a.find('div', attrs={'class': 'content-block'})
        Address.append(name.text)

    for i in soup.find_all('h4'):
        name3 = i
        Loc_name.append(name3.text)
        ## Lat n Lng

    for i in soup.find_all('script'):
        name3 = i
        Loc_name1.append(name3.text)

    Jvsc = Loc_name1[49][1351:2707]
    m = json.loads(Jvsc)

    lat = []
    lng = []
    loc = []
    for i in range(3, 8):
        print(i)
        k = m[str(i)]['lat']
        j = m[str(i)]['lng']
        s = m[str(i)]['address'].split(',')[2].split(" ")[2]
        lat.append(k)
        lng.append(j)
        loc.append(s)

    fullcontent = Address
    data = []
    for store in range(len(Address)):
        country = 'US'
        if ('Hours of Operation' in fullcontent[store]):
            op_hrs = fullcontent[store].split('Hours of Operation')[1].strip().replace('\n', '')
            op_hrs = op_hrs.replace('€', '')
        else:
            op_hrs = '<MISSING>'

        # print(raw_address)
        if ('(' in fullcontent[store]):
            phno = '(' + fullcontent[store].split('(')[1]
            alphabet = 'abcdefghijklmnopqrstuvwxyz@.!â€‹Â'
            phno = phno.lower()
            for letter in alphabet:
                phno = phno.replace(letter, '')
                if ('  ' in phno):
                    phno = phno.strip()
                    phno = phno.split("  ")[0]
                phno = [v for v in phno if v in '1234567890- ()']
                str1 = ""
                phno = str1.join(phno)
            raw_address = fullcontent[store].split('(')[0]
        else:
            phno = '<MISSING>'
            raw_address = fullcontent[store]
        try:
            tagged = usaddress.tag(raw_address)[0]

            # print("position is:",store)
        except:
            pass
        try:
            street_addr = tagged['BuildingName'] + " " + tagged['OccupancyType'] + " " + \
                          tagged['OccupancyIdentifier'].split('\n')[0]
        except:
            try:
                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                              tagged['StreetNamePostType'].split('\n')[0] + " " + tagged['OccupancyType'] + " " + \
                              tagged['OccupancyIdentifier'].split('\n')[0]
            except:
                try:
                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged[
                        'StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                except:
                    try:
                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                      tagged['StreetNamePostDirectional'].split('\n')[0] + " " + \
                                      tagged['StreetNamePostType'].split('\n')[0]
                    except:
                        try:
                            street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                          tagged['StreetNamePostDirectional'].split('\n')[0]
                        except:
                            try:
                                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                              tagged['StreetNamePostType'].split('\n')[0]
                            except:
                                try:
                                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName']
                                    street_addr = street_addr.strip()
                                except:
                                    pass
        loc_name_splitter = re.search(r'\d+', fullcontent[store]).group()
        location_name = fullcontent[store].split(loc_name_splitter)[0]
        location_name = location_name.strip()
        if (location_name == ''):
            location_name = Loc_name[store]
        try:
            state = tagged['StateName'].split(',')[1]
            city = tagged['PlaceName'] + " " + tagged['StateName'].split(',')[0]
        except:
            try:
                state = tagged['StateName']
                city = tagged['PlaceName']
                zipcode = tagged['ZipCode'].strip()

            except:
                pass

        lat1 = ''
        lng1 = ''
        for i in range(len(loc)):
            if (zipcode == loc[i]):
                lat1 = lat[i]
                lng1 = lng[i]

        data.append([
            'https://mightyfineburgers.com/',
            'https://mightyfineburgers.com/locations/',
            location_name,
            street_addr,
            city,
            state,
            zipcode,
            country,
            '<MISSING>',
            phno,
            '<MISSING>',
            lat1,
            lng1,
            op_hrs
        ])

    time.sleep(3)
    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()