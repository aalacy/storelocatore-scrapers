import csv
import requests
from bs4 import BeautifulSoup
import re
import json
# import sgzip


def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    # zips = sgzip.for_radius(100)
    return_main_object = []
    addresses = []

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    # it will used in store data.
    locator_domain = "https://www.gia.edu/"
    page_url = "<MISSING>"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    # print("zip_code == " + zip_code)
    r = requests.get('https://www.gia.edu/otmm_wcs_int/getRetailerLocations.jsp?reqUrl=https://webapps.gia.edu/RetailerLookUpService/retailerLookup.do&Latitude=33.1412124&Longitude=-117.32051230000002&Radius=100000&Stores=70000', headers=headers)
    json_data = r.json()
    myvalues = [i['results'] for i in json_data if 'results' in i]
    i= myvalues.pop(0)
    for x in i:
        country_code = x['address']['country']


        # print(ca_zip_list,us_zip_list)
        if  "US" == country_code or "us" == country_code or "Us" == country_code or "u.s." == country_code or "U.S." == country_code or "usa" == country_code or "USA" == country_code or "United States" == country_code =="United States Virgin Islands" == country_code or "U.S.A." == country_code or "u.s.a" == country_code or "United States of America" == country_code or "U.S. Virgin Islands" == country_code or "UNITED STATES" == country_code or "Canada" == country_code  or "Canada." == country_code or "CANADA" == country_code:


            if "" != x['address']['zip']:
                # print(x['address']['zip'],country_code)
                if "Canada" in country_code or "CANADA" in country_code:
                    zipp = x['address']['zip'].replace('/ Ontario','').upper().replace('-',' ')
                    country_code = "CA"
                    # print(country_code,zipp)
                else:
                    zip = x['address']['zip'].replace('CA','').replace('\\uFFFD','').strip()
                    # print(zip)
                    # print(len(zip))
                    # print('~~~~~~~~~~~~~~~~~~~~~`')
                    if len(zip) ==3:

                        zipp = "00"+zip
                        country_code = "US"

                    elif len(zip) ==4:
                        zipp = "0"+zip
                        country_code = "US"
                    elif len(zip) == 7:

                        zipp = zip
                        country_code = "CA"

                    else:
                        zipp = zip
                        country_code = "US"
                    # print(zipp)


            else:
                #
                if "Canada" in country_code or "CANADA" in country_code:
                    zipp = "<MISSING>"
                    country_code = "CA"

                else:
                    zipp = "<MISSING>"
                    country_code = "US"
                    # print("zipp === "+x['address']['zip'],country_code)
                    # print(country_code,zipp)







            store_number = x['id']
            location_name = x['storename'].replace('\\','').capitalize().strip()
            street_address = x['address']['street'].replace('\\','').replace('>','').capitalize().strip()
            # print(street_address)
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            city = x['address']['city'].split(',')[0].replace('\\','').replace('u00E9','e').replace('u00C8','c').capitalize().strip()
            state =x['address']['state'].replace('.','').strip()
            lat = x['address']['latitude']
            lng = x['address']['longitude']
            if "0" == str(lat)  or "0" == str(lng):
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            else:
                latitude = lat
                longitude = lng
            # print(latitude,longitude)
            hours = x['storehours']
            h = []
            for key,value in hours.items():
                h1 = "{}:{}".format(key, value)
                if "" == value:
                    h1 = "<MISSING>"
                else:

                    h.append(h1)
            if h !=[]:
                hours_of_operation = " ".join(h).replace('moned:','to ').replace('tueed','to ').replace('weded:','to ').replace('thued:','to ').replace('fried:','to ').replace('sated:','to ').replace('suned:Closed','').replace('st','').replace('suned:','to ').strip()
            else:
                hours_of_operation = "<MISSING>"
            # print(hours_of_operation)
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            store = ["<MISSING>" if x == "" or x ==
                     None else x for x in store]
            # store = [x if x else "<MISSING>" for x in store]
            # print(store[1:3])

            if store[2] in addresses:
                continue
            addresses.append(store[2])


            # print(state)
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            return_main_object.append(store)


    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


