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
    addresses = []
    base_url = "https://bluesushisakegrill.com/"
    page_url = "https://bluesushisakegrill.com/locations"
    r = requests.get(page_url)
    soup = BeautifulSoup(r.text, "lxml")
    store_name = []
    store_detail = []
    return_main_object = []
    name1 = []
    data = soup.find_all("div", {"class": "locations-city"})

    for i in data:
        p = i.find_all("div", {"class": "locations-item-details"})
        name = i.find_all("h3", {"class": "locations-item-title"})
        for j in name:
            name1.append(j.text)
        for index, j in enumerate(p):
            tem_var = []
            if len(j.a['href'].split('@')) == 2:
                lat = j.a['href'].split('@')[1].split(',')[0]
                lon = j.a['href'].split('@')[1].split(',')[1]

            else:
                lat = j.a['href'].split("ll=")[-1].split("+")[0]
                lon = j.a['href'].split("ll=")[-1].split("+")[1]
                # print(j.a['href'].split("ll=")[-1].split("+"))
            st = list(j.stripped_strings)[0]
            city = list(j.stripped_strings)[1].split(",")[0]
            state_list = list(j.stripped_strings)[1].split(",")
            if "Coming Soon :" in " ".join(state_list):
                continue
            # print(state_list)
            state = list(j.stripped_strings)[1].split(",")[1].split()[0]
            zip1 = list(j.stripped_strings)[1].split(",")[1].split()[1]
            phone = list(j.stripped_strings)[2]
            hours = " ".join(list(j.stripped_strings)[3:])

            tem_var.append("https://bluesushisakegrill.com")
            tem_var.append(name1[index])
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(lat)
            tem_var.append(lon)
            tem_var.append(hours)
            tem_var.append(page_url)
            # print("data == " + str(tem_var))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            if tem_var[2] in addresses:
                continue
            addresses.append(tem_var[2])
            return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
