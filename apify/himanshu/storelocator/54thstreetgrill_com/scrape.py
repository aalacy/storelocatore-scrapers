import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.54thstreetgrill.com"
    return_main_object = []
    r = session.get(base_url + "/54th-all-locations.html")
    soup = BeautifulSoup(r.text,"lxml")
    for parts in soup.find_all("li",{"class": "accordion-navigation"}):
        for semi_parts in parts.find_all("div",{"class": re.compile("columns small-12 medium-4")}):
            return_object = []
            store_request = session.get(base_url + semi_parts.find("h4").find("a")['href'])
            store_soup = BeautifulSoup(store_request.text,"lxml")
            locationDetails = store_soup.find("div",{"id": "locationDetails"})
            temp_list = list(locationDetails.find_all("p"))
            if len(temp_list) >= 2:
                hours_of_operation = temp_list[-2].text + " " + temp_list[-1].text
            for semi_semi_parts in semi_parts.find_all("h4",{"class": "local-name"}):
                temp_storename = list(semi_semi_parts.stripped_strings)
                location_name = temp_storename[-1].strip("()").split(",")[0]
            for semi_semi_parts in semi_parts.find_all("p",{"class": "local-address"}):
                temp_storeaddresss = list(semi_semi_parts.stripped_strings)
                street_address = temp_storeaddresss[0]
                st=temp_storeaddresss[1].split(",")[1].split(" ")
                if len(st)==3:
                    city = temp_storeaddresss[1].split(",")[0]
                    state = temp_storeaddresss[1].split(",")[1].split(" ")[1]
                    store_zip = temp_storeaddresss[1].split(",")[1].split(" ")[2]
                else:
                    city = temp_storeaddresss[1].split(",")[0].split(" ")[0]
                    state = temp_storeaddresss[1].split(",")[0].split(" ")[1]
                    store_zip = st[-1]
                phone = temp_storeaddresss[2]
            return_object.append("https://www.54thstreetgrill.com")
            return_object.append(location_name)
            return_object.append(street_address)
            return_object.append(city)
            return_object.append(state)
            return_object.append(store_zip)
            return_object.append("US")
            return_object.append("<MISSING>")
            return_object.append(phone)
            return_object.append("54TH STREET")
            return_object.append("<INACCESSIBLE>")
            return_object.append("<INACCESSIBLE>")
            return_object.append(hours_of_operation)
            return_main_object.append(return_object)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
