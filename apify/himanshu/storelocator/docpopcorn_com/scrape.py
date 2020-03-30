import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'cookie': 'JSESSIONID=9217AF597D0DD6004601D8AB32186F36.10-10-13-93; __cfduid=d685d1a5af8a445be5e72384caf5fc0831566567206; acdc_currency=USD; acdc_vat=false; _ga=GA1.2.927202771.1566567207; _gid=GA1.2.1425395567.1566567207; fs_uid=rs.fullstory.com`MCY2V`6478010954842112:5185394409766912; csrfToken=d76b7905-c91b-4dd9-81ac-359c02179afa; acdc_region=US; ACDC_LOCALE=EN; acdc_disclaimer=true; _gat=1'
    }

    # print("soup ===  first")

    base_url = "https://www.docpopcorn.com"
    r = session.get("https://www.docpopcorn.com/location-finder.html?location=59314&pageNumber=1&resultsPerPage=1000",
                     headers=headers)
    # soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "docpopcorn"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    location_url_list = []

    json_data = r.json()

    # print("data === " + str(len(json_data['locations'])))

    for address_list in json_data['locations']:
        # print("address_list === " + str(address_list))
        location_name = address_list['title']
        street_address = address_list['street1']
        if address_list['street2'] is not None:
            street_address += " " + address_list['street2']
        phone = address_list['phone']
        city = address_list['city']
        state = address_list['state']
        zipp = address_list['postalCode']
        country_code = 'US'
        longitude = address_list['latLng']['lng']
        latitude = address_list['latLng']['lat']

        if phone is None or len(phone) == 0:
            phone = "<MISSING>"

        # print("phone === "+phone)
        
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]
        store = ["<MISSING>" if x == "" or x == " " else x for x in store]

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
