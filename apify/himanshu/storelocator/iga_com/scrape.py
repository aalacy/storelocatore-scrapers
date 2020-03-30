import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
# import html5lib



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    zips = sgzip.coords_for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    # it will used in store data.
    locator_domain = "https://www.iga.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    page_no = 0
    isFinish = False
    while isFinish is not True:
        # r = session.get("https://www.iga.com/find-a-store?page=" + str(page_no) +
        #                  "&locationLat=" + str(lat) + "&locationLng=" + str(lng), headers=headers)

        r = session.get("https://www.iga.com/find-a-store?page=" + str(page_no) +
                         "&locationLat=38.65818091399883&locationLng=-115.09908940607174", headers=headers);
        # r1 = "https://www.iga.com/find-a-store?page=" + str(page_no) +"&locationLat=38.65818091399883&locationLng=-115.09908940607174"
        # print(r1)

        soup = BeautifulSoup(r.text, "html.parser")

        if soup.find('div', class_="store-card") == None:
            # print("None")
            isFinish = True
        else:
            # details = "page_no==" + str(page_no) + "==store_card==" +  str(soup.find_all('div', class_="store-card"))
            for details in soup.find_all('div', class_="store-card"):
                tag_address = details.find(
                    'div', class_='store-location')

                # dataurl = tag_address.find('a', class_='store-website-link')
                # if dataurl == None:
                #     dataurl = "<MISSING>"
                # else:
                #     page_url = dataurl['href'].strip()
                page_url = "<MISSING>"
                location_name = tag_address.find(
                    'div', class_="store-location-details").find('h3').text
                street_address = tag_address['data-address'].split(',')[
                    0].strip()
                city = tag_address['data-address'].split(',')[1].strip()
                state = tag_address['data-address'].split(',')[2].strip()
                if "Vail" == state or "Rio Rico" == state:
                    state = tag_address['data-address'].split(',')[-2].strip()
                zipp = tag_address['data-address'].split(',')[-1].strip()
                if len(zipp) == 4:
                    zipp = "0" + zipp
                # if "42106" == zipp or "42113" == zipp or "17328" == zipp:
                #     print(tag_address)
                #     print('~~~~~~~~~~~~~~~~~~~~~`')
                latitude = tag_address['data-lat']
                longitude = tag_address['data-long']
                phone = tag_address.find(
                    'p', class_="store-phone-fax").text.strip().split('- Main')[0]
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = ["<MISSING>" if x == "" else x for x in store]
                # print("data = " + str(store))
                # print(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)
        page_no += 1
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
