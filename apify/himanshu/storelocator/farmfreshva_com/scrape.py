import csv
import requests
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                        "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        
        print(data)
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.farmfreshva.com"
    req = requests.get(base_url)
    soup = BeautifulSoup(req.text, "lxml")
    addressColumn = soup.find("div",{"class": "et_pb_row et_pb_row_1"})
    locator_domain = base_url
    country_code = "US"
    store_number = "<MISSING>"
    location_type = soup.find("img", {"id":"logo"})["alt"]
    latitude = "<INACCESSIBLE>"
    longitude = "<INACCESSIBLE>"
    hours_of_op = "<MISSING>"
    data = []
    for address in addressColumn.findAll("div", {"class": "et_pb_column"}):
        row = []
        addr_split = address.find("div", {"class": "et_pb_blurb_container"}).text.split("\n")
        addr_split_removed_empty = []
        for x  in addr_split:
            if x != "":
                if "Chatham" not in x:
                    addr_split_removed_empty.append(x)
                else:
                    addr_split_removed_empty.append(x.split(".")[0])
                    addr_split_removed_empty.append(x.split(".")[1])
        streetAddr = addr_split_removed_empty[1].strip()
        phoneNo = addr_split_removed_empty[3].strip()
        city = addr_split_removed_empty[2].split(",")[0].strip()
        # state = addr_split_removed_empty[2].split(",")[1].strip()
        zipcode = addr_split_removed_empty[2].split(",")[2].strip()
        location_name = soup.title.text.split("|")[0] + "-" + city
        row.append(locator_domain)
        row.append(location_name)
        row.append(streetAddr)
        row.append(city)
        row.append('state')
        row.append(zipcode)
        row.append(country_code)
        row.append(store_number)
        row.append(phoneNo)
        row.append(location_type)
        row.append(latitude)
        row.append(longitude)
        row.append(hours_of_op)
        
        data.append(row)

    return data

def scrape():
    data = fetch_data()
    write_output(data)
scrape()

