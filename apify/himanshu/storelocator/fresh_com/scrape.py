import csv
import time

import requests
from bs4 import BeautifulSoup
import re
import json
from shapely.prepared import prep
from shapely.geometry import Point
from shapely.geometry import mapping, shape





def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
countries = {}


def getcountrygeo():
    data = requests.get("https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson").json()

    for feature in data["features"]:
        geom = feature["geometry"]
        country = feature["properties"]["ADMIN"]
        countries[country] = prep(shape(geom))


def getplace(lat, lon):
    point = Point(float(lon), float(lat))
    for country, geom in countries.items():
        if geom.contains(point):
            return country
    return "unknown"




def fetch_data():
    getcountrygeo()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/x-www-form-urlencoded',
    }

    addresses = []
    base_url = "https://www.fresh.com"
    # print(base_url)
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = ""

    r = requests.get("https://www.fresh.com/us/stores", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    results = soup.find('div',class_='storelocator_results')
    # print(results.prettify())
    for stores in results.find_all('div',class_='card store_card'):
        store_number ='<MISSING>'
        location_type = stores['data-store-type']
        location_name = stores.find('div',class_='card-header').a['aria-label'].capitalize()
        page_url = "https://www.fresh.com/us/stores"+stores.find('div',class_='card-header').a['href'].capitalize()
        latitude = stores.find('div',class_='card-header').a['data-store-coord'].split(',')[0].strip()
        longitude = stores.find('div',class_='card-header').a['data-store-coord'].split(',')[-1].strip()
        content = stores.find('div',class_='card-content').find('div',class_='card-body')
        hours = list(content.find('span',class_='store_hours').stripped_strings)
        if hours !=[]:
            hours_of_operation = " ".join(hours).strip()
        else:
            hours_of_operation = "<MISSING>"
        address = content.find('address')
        if address.find('div',class_='store_phone') !=None:
            phone = address.find('div',class_='store_phone').text.replace('Phone:','').strip()
        else:
            phone = "<MISSING>"
        adr = address.find('div',class_='show-in-map').text.strip().split('\n')
        
        adr = [i.strip() for i in adr]
        addr = []
        for element in adr:
            if element != '':
                addr.append(element)
        country_name = getplace(latitude, longitude)
        # city_name = getcity(latitude,longitude)
        # print("geo_url === " + str(country_name))
        # print(list(country_name))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
        if "United States of America" != country_name and "Canada" != country_name:
            continue
        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(" ".join(addr)))
        us_zipp =  " ".join(addr[0].split(',')[1:]) + " ".join(addr[1:])
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(us_zipp))
        if ca_zip_list:
            zipp = ca_zip_list[-1]
            country_code = "CA"

            street_address = addr[0].split(',')[0].strip()
            city = addr[1].strip()
            state = addr[2].strip().replace(',','').strip()
            if "Toronto" in state:
                state = addr[0].split(',')[1].split()[1].strip()
                city =  addr[0].split(',')[1].split()[0].strip()

        elif us_zip_list:
            # if len(addr) == 3:
            zipp= us_zip_list[0].strip()
            country_code = "US"
            st_address =addr[0].split(',')

            if len(st_address) ==4:
                street_address =  " ".join(st_address[:2]).strip()
                city = st_address[2].strip()
                state = st_address[-1].split()[0].strip()
                # print(state)
                # print(zipp+" | "+country_code+" | "+street_address+" | "+city+" | "+state)
            elif len(st_address) == 3:

                if "Suite 350" in "".join(st_address[1]) or "Suite#220" in "".join(st_address[1]):
                    street_address = " ".join(st_address[:2]).strip().replace('Woodmere','').replace('Austin','').strip().capitalize()

                else:
                    street_address =  st_address[0].strip().capitalize()

                if "N.W." != st_address[1]:
                    city = st_address[1].strip().replace('Suite 350','').replace(' Suite#220','').replace('NW','').strip().capitalize()

                else:
                    city = st_address[-1].split()[0].strip().replace('CA','').capitalize()
                if "Los Angeles CA" in city:
                    state= city.split()[-1].strip()
                else:
                    if len(st_address[-1].split()) >1:
                        state= st_address[-1].split()[0].strip().replace('.','').strip()
                    else:
                        state = "<MISSING>"
                if "Washington"  == state:
                    state = "DC"
                # print(zipp+" | "+country_code+" | "+street_address+" | "+city+" | "+state)
            elif len(st_address) == 2:
                state_list = re.findall(r' ([A-Z]{2}) ', str( " ".join(addr)))
                # print(state_list)
                try:
                    state = state_list[-1].strip()
                except:
                    state = "<MISSING>"
                if "CA" != addr[-2] and "TN" !=addr[-2] and "AZ" != addr[-2]:
                    city = addr[-2].strip().replace(',','').strip()

                else:
                    city = addr[-3].strip().replace(',','').strip()

                street_address = st_address[0].strip().replace('Portland','').replace('Atlantic City','').replace('New York','').replace('West Denville','').replace('Highland Park','').replace('Washington','').replace('Fairfax','').replace('Ft. Lauderdale','').replace('Dallas','').replace('Westfield','').replace('Atlanta','').replace('New Canaan','').replace('Tampa','').replace('Chicago','').replace('Woodbury','').replace('Bethesda','').replace('Wayne','').replace('Lynnfield','').replace(' Westlake hills','').replace('Birmingham','').replace('Hinsdale','').replace('Chicago','').replace('Philadelphia','').replace('Jacksonville','').replace('Lake Forest','').replace('Alexandria','').replace('Studio City','').replace('Santa Monica','').replace('Arlington','').replace('Corte Madera','').replace('nn Arbor','').replace('Bronxville','').strip()
                # print(street_address)
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')


            else:
                # print(addr)
                # print(len(addr))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                if len(addr) > 4:
                    street_address = addr[0].strip()+ " "+ addr[1].strip()

                else:
                    street_address = addr[0].strip()
                city = addr[-3].strip().replace(',','').strip()
                state = addr[-2].strip()
                # print(state)
                if "Washington DC" == state:
                    state = "DC"
                    # print(addr)
                # print(zipp+" | "+country_code+" | "+street_address+" | "+city+" | "+state)

        else:
            # print(ca_zip_list,us_zip_list)
            country_name = getplace(latitude, longitude)
            if "Canada" == country_name:
                country_code = "CA"

            else:
                country_code = "US"
            city = addr[1].strip()
            zipp_list= re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str( " ".join(addr)))
            if zipp_list != []:
                zipp = zipp_list[0]
            else:
                zipp = "<MISSING>"
            if len(addr[0].split(','))>1:

                street_address = "".join(addr[0].split(',')[:-1]).strip()
            else:
                street_address = addr[0].strip()
            # print( " ".join(addr))
            # print(addr[-1].isdigit())
            if addr[-1].isdigit():
                if len(addr[0].split(',')) > 1:
                    state = addr[0].split(',')[-1].split()[-2].replace('.','').strip()

                else:
                    state = "<MISSING>"
            else:
                state = addr[-1].strip()



        if "17600" in zipp or "10355" in zipp:
            zipp = "<MISSING>"
            # print(addr)
            # print("~~~~~~~~~~~~~~~~~")
        if "Vancouver" in state:
            state = addr[-3].strip()

        state = state.replace(",","").replace("2043","MA").replace("2840","RI").replace("6107","CT").replace("6901","CT").replace("Washington DC","DC").strip()
        zipp = zipp.replace("10250","<MISSING>").replace("40772","<MISSING>").replace("20530","<MISSING>").replace("26300","<MISSING>").replace("23161","<MISSING>").replace("11960","<MISSING>").replace("23501","<MISSING>").replace("17101","<MISSING>").replace("12669","<MISSING>").replace("11800","<MISSING>").replace("13350","<MISSING>").replace("13915","<MISSING>").replace("11240","<MISSING>").replace("17410","<MISSING>").replace("24201","<MISSING>").replace("15900","<MISSING>").replace("11731","<MISSING>").replace("21500","<MISSING>").replace("12000","<MISSING>").replace("27484","<MISSING>").replace("11252","<MISSING>").replace("14006","<MISSING>").replace("16535","<MISSING>").replace("19507","<MISSING>").replace("73505","<MISSING>").replace("15169","<MISSING>").replace("21725","<MISSING>").replace("12522","<MISSING>").replace("10300","<MISSING>").replace("19575","<MISSING>").replace("07520","<MISSING>")
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[2]) not in addresses:
            addresses.append(str(store[2]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
