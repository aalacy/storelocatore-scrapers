import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
# import json
# import sgzip
# import time



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []



    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    base_url = 'https://lotsa.com'
    locator_domain = "https://lotsa.com"
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



    r= session.get('https://lotsa.com/locations/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    # tag_address = soup_location.find(
    #             lambda tag: (tag.name == "a" ) and "View Location" in tag.text)
    for a in soup.find_all('a',class_='et_pb_custom_button_icon'):
        # print(a['href'])
        r_loc = session.get(base_url + a['href'],headers = headers)
        soup_loc= BeautifulSoup(r_loc.text,'lxml')
        page_url = base_url + a['href']
        div = soup_loc.find('div',class_="et_pb_row_3").find('div',class_='et_pb_text_inner')

        list_div = list(div.stripped_strings)
        # print(list_div)
        # print(len(list_div))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~')
        if len(list_div) != 3:
            phone = list_div[0]
            street_address = list_div[1]
            city = list_div[2].split(',')[0]
            state = list_div[2].split(',')[-1].split()[0]
            zipp = list_div[2].split(',')[-1].split()[-1]
            location_name = city +","+state
            hours_of_operation = " ".join(list_div[5:])

            coords = div.find(
                lambda tag: (tag.name == "a") and "Get Directions" in tag.text)['href'].split('=')
            # print(coords)
            # print(len(coords))
            # print('~~~~~~~~~~~~~~~~~~~~~')
            if len(coords) ==8:
                latitude = coords[1].split(',')[0]
                longitude = coords[1].split(',')[-1].split('&')[0]
            else:
                latitude = coords[0].split('@')[1].split(',')[0]
                longitude =coords[0].split('@')[1].split(',')[1].split(',')[0]
            # print(latitude,longitude)
        else:
            div = soup_loc.find('div',class_="et_pb_row_4").find('div',class_='et_pb_text_inner')
            # print(div.prettify())
            list_add=list(div.stripped_strings)
            # print(list_add)
            phone = "".join(list_add[0:2])
            street_address = list_add[2]
            city = list_add[3].split(',')[0]
            state =  list_add[3].split(',')[-1].split()[0]
            zipp = list_add[3].split(',')[-1].split()[-1]
            location_name = city +","+state
            hours_of_operation = " ".join(list_add[6:])
            latitude = div.find(
                lambda tag: (tag.name == "a") and "Get Directions" in tag.text)['href'].split('=')[0].split('@')[1].split(',')[0]
            longitude = div.find(
                lambda tag: (tag.name == "a") and "Get Directions" in tag.text)['href'].split('=')[0].split('@')[1].split(',')[1]
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        store = ["<MISSING>" if x == "" else x for x in store]

        print("data = " + str(store))
        print(
            '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
