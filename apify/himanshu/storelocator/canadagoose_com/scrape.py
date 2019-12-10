
import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    arr = ["US", "CA"]
    return_main_object = []
    return_main_object1 = []
    addresses = []
    for i in range(len(arr)):
        base_url1 = 'https://hosted.where2getit.com/canadagoose/ajax?xml_request=<request><appkey>8949AAF8-550E-11DE-B2D5-479533A3DD35</appkey><formdata id="getlist"><objectname>StoreLocator</objectname><limit>5000</limit><order>rank::numeric</order><where><city><ne>Quam</ne></city><country><eq>' + \
            str(arr[i]) + '</eq></country></where><radiusuom></radiusuom></formdata></request>'
        r1 = requests.get(base_url1)
        main_soup1 = BeautifulSoup(r1.text, "lxml")
        for poi in main_soup1.find_all('poi'):
            locator_domain = "https://www.canadagoose.com/"
            location_name = poi.find("name").text.strip()
            street_address = poi.find("address1").text.strip()
            city = poi.find("city").text.strip()
            latitude = poi.find("latitude").text.strip()
            longitude = poi.find("longitude").text.strip()
            phone = poi.find("phone").text.strip()
            state = poi.find("state").text.strip()
            zipp = poi.find("postalcode").text.strip()
            hours_of_operation = "<MISSING>"
            country_code = poi.find("country").text.strip()
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            page_url = "https://www.canadagoose.com/ca/en/find-a-retailer/find-a-retailer.html"
            if len(zipp) == 4:
                zipp = "0" + zipp
            if zipp == "0":
                zipp = "<MISSING>"
            if "7017" == location_name:
                location_name = city

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[1]) + str(store[2]) not in addresses and country_code:
                addresses.append(str(store[1]) + str(store[2]))

                store = [str(x).encode('ascii', 'ignore').decode(
                    'ascii').strip() if x else "<MISSING>" for x in store]
                if "SoHo 101 Wooster Street" in store or "800 Boylston St" in store or "6455 Macleod Trail SW" in store or "1200 Morris Turnpike" in store or "1020 Saint-Catherine St W" in store:
                    pass
                #print("data = " + str(store))
                #print(
                    # '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store

    base_url = "https://www.canadagoose.com/ca/en/find-a-retailer/find-a-retailer.html"
    addresses = []
    r = requests.get(base_url)
    main_soup = BeautifulSoup(r.text, "lxml")
    for store in main_soup.find_all('div', class_='store'):
        locator_domain = "https://www.canadagoose.com/"
        location_name = list(store.find(
            'h3', {'class': 'section-break'}).stripped_strings)[-1].strip()
        street_address = store.find(
            'span', {'itemprop': "streetAddress"}).text.strip()
        street_address = re.sub(' +', ' ', street_address)
        city = store.find('span', {'itemprop': "addressLocality"}).text.strip()
        state = store.find('span', {'itemprop': "addressRegion"}).text.strip()
        zipp_tag = store.find('span', {'itemprop': "postalCode"}).text.strip()
        phone = store.find('span', {'itemprop': "telephone"}).text.strip()
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        ca_zip_list = re.findall(
            r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp_tag))
        us_zip_list = re.findall(re.compile(
            r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp_tag))

        country_code = ""
        if ca_zip_list:
            zipp = ca_zip_list[-1]
            country_code = "CA"

        if us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"
        else:
            pass
        page_url = store.find('a', {'class': "more-info"})['href']
        r_loc = requests.get(page_url)
        soup_loc = BeautifulSoup(r_loc.text, 'lxml')
        if soup_loc.find('div', class_='store-info') != None:
            store_info = list(soup_loc.find(
                'div', class_='store-info').stripped_strings)
            hours_of_operation = " ".join(store_info).split(
                '.com')[-1].replace('Directions', "").strip()
            coord = soup_loc.find('div', class_='store-info').find(lambda tag: (
                tag.name == 'a') and "Directions" in tag.text.strip())
            if coord == None:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            else:
                latitude = coord['href'].split('@')[-1].split(',')[0]
                longitude = coord['href'].split('@')[-1].split(',')[1]

        else:
            pass
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[1]) + str(store[2]) not in addresses and country_code:
            addresses.append(str(store[1]) + str(store[2]))

            store = [str(x).encode('ascii', 'ignore').decode(
                'ascii').strip() if x else "<MISSING>" for x in store]
            #print("data = " + str(store))
           # print(
                # '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
