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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        'Content-Type': 'application/json; charset=UTF-8'
    }

    addresses = []

    base_url = "https://www.cox.com"
    r = session.get("https://www.cox.com/webapi/aem/coxretaillocations", headers=headers)
    # soup = BeautifulSoup(r.text, "lxml")
    json_data = r.json()

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
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    # print('json data = ' + str(json_data))

    day_list = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]

    for address_list in json_data['locations']:
        # print("address_list ==== " + str(address_list['hours']))
        if "hours" in address_list:
            
            hour_list = address_list['hours'].split(',')

            hours_of_operation = ""

            for hour_item in hour_list:
                day = hour_item.split(':')[0]

                if hours_of_operation == "":
                    for i in range(int(day))[1:]:
                        # print("day === "+ str(i))
                        hours_of_operation += str(day_list[i-1]) +" - Closed, "

                morning = ":".join(hour_item.split(':')[1:3])
                evening = ":".join(hour_item.split(':')[3:])
                if day != "":
                    hours_of_operation += str(day_list[int(day)-1]) +" - "+ morning +" to "+evening +", "
                else:
                    hours_of_operation = "<MISSING>"

        # print("hour_item ==== "+ str(hours_of_operation) )
        city = address_list['city']
        country_code = address_list['countryCode']
        state = address_list['state']
        zipp = address_list['zip']
        street_address = address_list['address']
        if "address2" in address_list:
            street_address += ", "+address_list['address2']

        location_name = address_list['locationName']
        phone = ''
        if "phone" in address_list :
            phone = address_list['phone']
        latitude = str(address_list['displayLat'] if "displayLat" in address_list else address_list["yextRoutableLat"])
        longitude = str(address_list['displayLng'] if "displayLng" in address_list else address_list["yextRoutableLng"])
        page_url = address_list['displayWebsiteUrl']
        store_number = address_list['id']
        location_type =  location_name.split(" (Military")[0].split(" - ")[0].split(" , ")[0]
        if "Cox Business" in location_type:
            store_number = "<MISSING>"
        store = [locator_domain, location_name +" "+ city , street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation.replace("SUNDAY - 0:00 to 0:00, MONDAY - 0:00 to 0:00, TUESDAY - 0:00 to 0:00, WEDNESDAY - 0:00 to 0:00, THURSDAY - 0:00 to 0:00, FRIDAY - 0:00 to 0:00, SATURDAY - 0:00 to 0:00,","<MISSING>"), page_url.replace("http://coxbusiness.com","<MISSING>").replace("[[Pages URL]]","<MISSING>")]

        if store[2] + store[-3] not in addresses:
            addresses.append(store[2] + store[-3])

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
