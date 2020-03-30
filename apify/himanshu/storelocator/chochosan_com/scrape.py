import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "https://www.chochosan.com/location"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    base_url1 = "https://www.chochosan.com/location-map"
    r = session.get(base_url1, headers=headers)
    soup1 = BeautifulSoup(r.text, "lxml")

    stores1 = soup1.find_all(
        "div", {"class": "txtNew", "data-packed": "false", "id": "comp-jspg5178"})
    stores2 = soup1.find_all(
        "div", {"class": "txtNew", "data-packed": "false", "id": "comp-jspgftft"})
    stores3 = soup1.find_all(
        "div", {"class": "txtNew", "data-packed": "false", "id": "comp-jsqnmpe2"})
    stores4 = soup1.find_all(
        "div", {"class": "txtNew", "data-packed": "false", "id": "comp-jsqntvax"})

    store_name = []
    store_detail = []
    return_main_object = []
    hours = []

    for i in stores1:
        hours.append(" ".join(list(i.stripped_strings)).replace(
            "Kisho Valencia Hours", "").replace("Cho Cho San Encino Hours", ""))

    for i in stores2:
        hours.append(" ".join(list(i.stripped_strings)).replace(
            "Kisho Valencia Hours", "").replace("Cho Cho San Thousand Oaks Hours", ""))

    for i in stores3:
        hours.append(" ".join(list(i.stripped_strings)).replace(
            "Kisho Valencia Hours", "").replace("Cho Cho San Tarzana ", ""))

    for i in stores4:
        hours.append(" ".join(list(i.stripped_strings)).replace(
            "Kisho Valencia Hours", ""))

    stores = soup.find_all(
        "div", {"class": "txtNew", "data-packed": "false", "data-min-height": "106"})

    for i in stores:
        tem_var = []
        phone = list(i.stripped_strings)[-1]
        store_name.append(" ".join(list(i.stripped_strings)[
                          :3][:-1]).replace("(Teppan,Sushi Bar,Dining,Lounge)", ""))
        st = (" ".join(" ".join(list(i.stripped_strings)[2:][:-1]).replace("(Sushi Bar & Dining) ", "").replace(
            "(Sushi Bar Only) ", "").replace("(Teppan,Sushi Bar,Dining ) ", "").split('CA')[0].split(".")[:-1]))
        city = (" ".join(list(i.stripped_strings)[2:][:-1]).replace("(Sushi Bar & Dining) ", "").replace(
            "(Sushi Bar Only) ", "").replace("(Teppan,Sushi Bar,Dining ) ", "").split('.')[-1]).split(",")[0].strip()
        state = (" ".join(list(i.stripped_strings)[2:][:-1]).replace("(Sushi Bar & Dining) ", "").replace(
            "(Sushi Bar Only) ", "").replace("(Teppan,Sushi Bar,Dining ) ", "").split('.')[-1]).split(",")[-1].split()[0].strip()
        zipp = (" ".join(list(i.stripped_strings)[2:][:-1]).replace("(Sushi Bar & Dining) ", "").replace(
            "(Sushi Bar Only) ", "").replace("(Teppan,Sushi Bar,Dining ) ", "").split('.')[-1]).split(",")[-1].split()[-1].strip()

        tem_var.append(st)
        # print(tem_var[0])
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipp)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        store_detail.append(tem_var)

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.chochosan.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append(hours[i])
        store.append("https://www.chochosan.com/location")
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
