import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import calendar


def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    # zips = sgzip.for_radius(100)
    zips = sgzip.coords_for_radius(100)
    return_main_object = []
    addresses = []

    headers = {'Accept': '* / *',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
               'Connection': 'keep-alive',
               'Cookie': 'TS016c456a=010521ad2d62cb06fe3f003d01473b8c2bfa3c16178f9c147711842e156470d7b68fba2b4fcd3b60e25e4aeb1391a17b5dae95d8ccc3256fe76062d9af67e2399bd1a9fa32; BlueStripe.PVN=6a880002f350; ASP.NET_SessionId=pcby3dvhoc52sb4ryiwaknto; _gcl_au=1.1.1294638080.1569047565; _ga=GA1.2.888388994.1569047565; _fbp=fb.1.1569047566625.1310386045; _mibhv=anon-1569047567093-3406298552_8116; SC_ANALYTICS_GLOBAL_COOKIE=9cb0a81547e7405d98b454819d6d0245|True; _st_bid=1bb78b40-d13b-11e9-815e-91e5fd4a2043; TS01b1b9c7=010521ad2da1e055aaa292146581cbe09ccc88f0e81c88902237ecdc47e4635b96b2e76c5f7b03b2520ea09d9af72318c421e7f34de24f85ca96b277048bc833df0f18c131ee033252c97b784b4aacae3c163c4eb0cdc42ac38d87a258d8da987098a87be4; _gid=GA1.2.574249161.1569223649; _gat_gtag_UA_1177750_1=1; dtLatC=4; pageviewCount=3; _dc_gtm_UA-1177750-1=1; _st=1bb78b40-d13b-11e9-815e-91e5fd4a2043.a0c78e30-dc39-11e9-b25a-5d8890877954.8663178837.(866) 317-8837.+18663178837.1.8669036333...1569224387.1569234587.600.10800.30.0....0....1...raymondjames^com.UA-1177750-1.888388994^1569047565.33.; dtCookie=09B83C92E1115437DC4E4BBFA9D18CAA|UmF5bW9uZGphbWVzLmNvbXwx; dtPC=-',
               'Host': 'www.raymondjames.com',
               'Referer': 'https://www.raymondjames.com/find-an-advisor?citystatezip=&lastname=',
               'Sec-Fetch-Mode': 'cors',
               'Sec-Fetch-Site': 'same-origin',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
               'X-Requested-With': 'XMLHttpRequest'
               }

    # it will used in store data.
    locator_domain = "https://getgocafe.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "rickersrewards"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    skip = 0

    isFinish = False
    while isFinish is not True:
        r = requests.get(
            "https://getgocafe.com/api/sitecore/locations/getlocationlistvm?q=banner:(code+(GG))&skip=" + str(skip) + "&top=5&orderBy=geo.distance(storeCoordinate,%20geography%27POINT(72.8302%2021.1959)%27)%20asc", headers=headers)
        # print("json==" + r.text)
        # # print(str(page))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")

        json_data = r.json()

        if skip > 262:
            isFinish = True
            break

        else:
            if json_data['Locations'] != []:
                for x in json_data['Locations']:
                    location_name = x['Name']
                    if x['Address']['lineTwo'] == None or x['Address']['lineTwo'] == '-':
                        street_address = x['Address']['lineOne']
                        # print(street_address)
                    else:
                        street1 = x['Address']['lineOne']
                        street2 = x['Address']['lineTwo']
                        street12 = street1, street2
                        street_address = " ".join(street12)
                        # print(street_address)
                    city = x['Address']['City']
                    state = x['Address']['State']['Abbreviation']
                    zipp = x['Address']['Zip']
                    latitude = x['Address']['Coordinates']['Latitude']
                    longitude = x['Address']['Coordinates']['Longitude']
                    # print(city, state, latitude, longitude)
                    phone1 = x['TelephoneNumbers']
                    ph = [y['DisplayNumber']
                          for y in phone1 if 'DisplayNumber' in y]
                    phone = "  or  ".join(ph)
                    # print(phone)

                    hour1 = x['HoursOfOperation']
                    # h1 = [y['DayNumber']
                    #       for y in hour1 if 'DayNumber' in y]
                    hours = [y['HourDisplay']
                             for y in hour1 if 'HourDisplay' in y]
                    # hours_of_operation = "  ".join(hours)
                    day = list(calendar.day_abbr)

                    hours_of_operation = day[0] + "   " + hours[0] + "  " + day[1] + "   " + hours[1] + "  " + day[2] + "   " + hours[2] + "  " + day[3] + \
                        "   " + hours[3] + "  " + day[4] + "   " + hours[4] + "  " + \
                        day[5] + "   " + hours[5] + "  " + \
                        day[6] + "   " + hours[6]
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation]
                    store = ["<MISSING>" if x == "" else x for x in store]
                    # print("data = " + str(store))
                    # print(
                    #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                    return_main_object.append(store)

        skip += 5
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
