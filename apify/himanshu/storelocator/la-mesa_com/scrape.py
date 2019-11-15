import csv
import requests
from bs4 import BeautifulSoup
import re
# import json
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
    # zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    # it will used in store data.
    base_url = 'https://la-mesa.com/'
    locator_domain = "https://la-mesa.com/"
    page_url = "<MISSING>"
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
    page_url = ''

    coords = requests.get('https://la-mesa.com/locations/',headers = headers)
    c_soup = BeautifulSoup(coords.text,'lxml')
    c1 = []
    c2 = []
    for coord in c_soup.find_all('div',class_='et_pb_map_pin'):
        lat = coord['data-lat'].strip()
        lng = coord['data-lng'].strip()
        c1.append(lat)
        c2.append(lng)


    r = requests.get('https://la-mesa.com/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    ul= soup.find('ul',{'id':'top-menu'})
    li = soup.find(lambda tag: (tag.name == "li") and "Locations" in tag.text).find('ul',class_='sub-menu')
    for a in li.find_all('a'):
        page_url = a['href']
        r_loc = requests.get(a['href'],headers = headers)
        soup_loc = BeautifulSoup(r_loc.text,'lxml')
        div = soup_loc.find('div',class_='et_pb_row et_pb_row_0')
        address= div.find('div',class_='et_pb_blurb_description')
        list_address= list(address.stripped_strings)
        location_name =list_address[0].strip()
        street_address = list_address[1].strip()
        city = list_address[2].split(',')[0].strip()
        state = list_address[2].split(',')[-1].split()[0].strip()
        zipp = list_address[2].split(',')[-1].split()[-1].strip()
        phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(" ".join(list_address[3:])))[0].strip()
        hours = soup_loc.find(lambda tag: (tag.name == "h4") and "Hours of Operation" in tag.text).find_next('div',class_='et_pb_blurb_description')
        list_hours = list(hours.stripped_strings)
        hours_of_operation = "  ".join(list_hours).strip()
        latitude = c1.pop(0)
        longitude = c2.pop(0)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = [x if x else "<MISSING>" for x in store]

        if store[2] in addresses:
            continue
        addresses.append(store[2])

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)




    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
