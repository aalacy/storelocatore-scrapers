import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "https://www.affinia.com"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("li", {"id": "menu-item-2809"}):
        for semi_part in parts.find_all("ul", {"class": "sub-menu"}):
            for inner_semi_part in semi_part.find_all("li", {"class": "menu-item"}):
                location_name = inner_semi_part.find("a").text
                store_request = session.get(inner_semi_part.find("a")['href'])
                store_soup = BeautifulSoup(store_request.text, "lxml")

                for in_semi_part in store_soup.find_all("address", {"class": "footer__top-section footer__top-section--left"}):
                    return_object = []
                    dir = store_soup.find("div", {"id": "neighborhood-map"})

                    temp_storeaddresss = list(in_semi_part.stripped_strings)
                    temp_storeaddresss = [w.replace('\xa0', ' ') for w in temp_storeaddresss]
                    lat = dir["data-latitude"]
                    lag = dir["data-longitude"]

                    if 'Contact' in temp_storeaddresss :
                      temp_storeaddresss.remove('Contact')

                    if(len(temp_storeaddresss) == 6):
                        street_address = temp_storeaddresss[0]+' '+ temp_storeaddresss[1]
                        city = temp_storeaddresss[2]
                        state = temp_storeaddresss[3].split(" ")[0]
                        store_zip = temp_storeaddresss[3].split(" ")[1]
                        phone = temp_storeaddresss[4]
                    else:
                        add = temp_storeaddresss[1]
                        state_zip = add.split(",")
                        state = state_zip[1].split(" ")[1]
                        store_zip = state_zip[1].split(" ")[2]

                        new_add = state_zip[0].split(" ")
                        if(len(new_add) == 2):
                            city =  new_add[-2]+ " "+ new_add[-1]
                            street_address = temp_storeaddresss[0]
                        else:
                            city = new_add[-2] + " " + new_add[-1]
                            street_address = temp_storeaddresss[0]+" "+ new_add[0]+ " "+ new_add[1]
                        phone = temp_storeaddresss[2]

                return_object.append(base_url)
                return_object.append(location_name)
                return_object.append(street_address)
                return_object.append(city)
                return_object.append(state)
                return_object.append(store_zip)
                return_object.append("US")
                return_object.append("<MISSING>")
                return_object.append(phone)
                return_object.append("Affinia Hotel & suites")
                return_object.append(lat)
                return_object.append(lag)
                return_object.append("<MISSING>")
                return_main_object.append(return_object)
           
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)

scrape()


