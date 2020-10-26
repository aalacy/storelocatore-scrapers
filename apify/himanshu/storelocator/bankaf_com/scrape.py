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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }



    base_url = "https://www.bankaf.com"
    r = session.get("https://www.bankaf.com/home/locations.html", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = ""
    location_type = "bankaf"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = ""

    temp_location_list1 = soup.text.split("name:")

    temp_location_list2 = []
    for temp_loc in temp_location_list1[1:]:
        temp_location_list2.append(temp_loc.split('};')[0])

    for final_location_data in temp_location_list2:

        location_name = final_location_data.split(',')[0]
        latitude = final_location_data.split('lat: "')[1].split('",')[0]
        longitude = final_location_data.split('lng: "')[1].split('",')[0]
        phone = final_location_data.split('<a href=\'tel:')[1].split('\'>')[0].replace("\n", "")
        street_address = final_location_data.split('<em>')[1].split('</em><br>\\')[0].replace("</em><br> \\", "").replace('\n','').strip()
        city = final_location_data.split('<em>')[2].split('</em><br>\\')[0].split(',')[0]
        state = final_location_data.split('<em>')[2].split('</em><br>\\')[0].split(',')[1].strip().split(' ')[0]
        zipp = final_location_data.split('<em>')[2].split('</em><br>\\')[0].split(',')[1].strip().split(' ')[1].replace("</em><br>","")
        country_code = 'US'

        try:
            hours_of_operation = final_location_data.split('<strong>Hours of Operation:</strong><br>\\')[1].replace(
                '<br>\\', "").replace("\"", "")
        except:
            hours_of_operation = final_location_data.split(' <strong>Lobby Hours:</strong><br/>\\')[1].replace('<br>\\',
                                                                                                               "").replace(
                "<strong>", "").replace("</strong>", "").replace("\"", "")

        hours_of_operation = hours_of_operation.replace("\n", "").strip().replace("  ", "").replace("<span>","").replace("</span>"," ").replace("<br>"," ")

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
