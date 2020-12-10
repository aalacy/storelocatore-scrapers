import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('risingroll_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        # logger.info("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://risingroll.com"
    r = session.get(
        "https://risingroll.com/locations-menu/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # logger.info(soup.prettify())

    return_main_object = []

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zip = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for val in soup.find_all('div', class_="et_section_regular"):
 
        for location in val.find_all('div', {'id': 'locdesc'}):
            if location != []:
                location_name = location.find('h1').text
                location_details = location.find('a')
                r_location = session.get(
                    base_url + location_details['href'], headers=headers)
                page_url = base_url + location_details['href']
                soup_loc = BeautifulSoup(r_location.text, "lxml")
                supersup=soup_loc.find("iframe",{"src":re.compile("mapquest.com")})['src']
                try:
                    ph = str(soup_loc.find("div",{"class":"et_pb_column_5"})).split("<strong>P")[1]
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(ph))
                    phone = phone_list[0]
                except:
                    phone = "<MISSING>"
                    pass
                r_locations = BeautifulSoup(session.get(supersup, headers=headers).text,'lxml')
                data = json.loads(r_locations.find("script",{"id":"MQPlace"}).text)
                location_name = (soup_loc.find("div",{"class":"et_pb_column_5"}).find("strong").text)
                street_address=data['address']['address1']
                city=data['address']['locality']
                state=data['address']['region']
                zip=data['address']['postalCode']
                latitude = data['displayLatLng']['lat']
                longitude = data['displayLatLng']['lng']
                if "https://risingroll.com/gainesville-fl-university-of-florida/" in page_url:
                    phone = "352-294-2213"

                if "https://risingroll.com/dunwoody-ga/" in page_url:
                    phone = "770.698.8000"
                store = [locator_domain, location_name.strip().replace("\n",' '), street_address, city, state, zip, country_code,
                                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

                store = ["<MISSING>" if x ==
                            "" else x for x in store]
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store






def scrape():
    data = fetch_data()
    write_output(data)


scrape()
