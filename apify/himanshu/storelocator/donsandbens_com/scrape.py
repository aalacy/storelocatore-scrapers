import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )

        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess = []
    match_dict = {}
    base_url = "https://donsandbens.com/locations/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find_all("div", {"class": "elementor-post__card"}):
        url = link.find("a")["href"]
        r1 = session.get(url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        check_phone = list(
            soup1.find(
                "div", {"class": "elementor-text-editor elementor-clearfix"}
            ).stripped_strings
        )[-2]
        match_dict[check_phone] = url
    json_data = json.loads(
        str(soup)
        .split("['web_data/donsandben.json'] = JSON.parse(")[1]
        .split('");')[0]
        .strip('"')
        .replace("\\", "")
    )
    for val in json_data["merchant_configs"]:
        location_name = val["merchant"]["name"]
        street_address = val["merchant"]["address"]["address_properties"][
            "street_address"
        ].replace("Address:", "")
        city = val["merchant"]["address"]["address_properties"]["city"]
        state = val["merchant"]["address"]["address_properties"]["state"]
        zipp = val["merchant"]["address"]["address_properties"]["zip"]
        country_code = val["merchant"]["address"]["country_code"]
        temp_phone = val["merchant"]["phone_number"]
        phone = "(" + temp_phone[:3] + ")" + temp_phone[3:6] + "-" + temp_phone[6:]
        phone = phone.replace("(210)399-1283", "(210)339-1283")
        latitude = val["merchant"]["address"]["address_properties"]["lat"]
        longitude = val["merchant"]["address"]["address_properties"]["lng"]
        hours_of_operation = "Mon to Sat 11:00AM-8:00PM, Sun-Closed"
        if phone in match_dict:
            page_url = match_dict[phone]
            match_dict.pop(phone)

        store = []
        store.append("https://donsandbens.com/")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append("<MISSING>")
        store.append(phone)
        store.append("Dons and Bens")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store

    for val in match_dict.values():
        page_url = val
        soup2 = BeautifulSoup(session.get(page_url).text, "lxml")
        location_name = (
            "Don's and Ben's Liquor "
            + soup2.find(
                "h4", {"class": "elementor-heading-title elementor-size-default"}
            ).text
        )
        addr = list(
            soup2.find(
                "div", {"class": "elementor-text-editor elementor-clearfix"}
            ).stripped_strings
        )
        street_address = addr[0].split("•")[0].replace("Address:", "").strip()
        city = addr[0].split("•")[1].strip().split(",")[0]
        state = addr[0].split("•")[1].strip().split(",")[1].strip().split(" ")[0]
        zipp = addr[0].split("•")[1].strip().split(",")[1].strip().split(" ")[1]
        phone = addr[2]
        hours_of_operation = "Mon to Sat 11:00AM-8:00PM, Sun-Closed"

        store = []
        store.append("https://donsandbens.com/")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("Dons and Bens")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours_of_operation)
        store.append(page_url)
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
