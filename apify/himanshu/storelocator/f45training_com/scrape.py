import re
import json
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import usaddress as usadr

tm = {
    "Recipient": "recipient",
    "AddressNumber": "address1",
    "AddressNumberPrefix": "address1",
    "AddressNumberSuffix": "address1",
    "StreetName": "address1",
    "StreetNamePreDirectional": "address1",
    "StreetNamePreModifier": "address1",
    "StreetNamePreType": "address1",
    "StreetNamePostDirectional": "address1",
    "StreetNamePostModifier": "address1",
    "StreetNamePostType": "address1",
    "BuildingName": "address1",
    "CornerOf": "address1",
    "IntersectionSeparator": "address1",
    "LandmarkName": "address1",
    "USPSBoxGroupID": "address1",
    "USPSBoxGroupType": "address1",
    "OccupancyType": "address1",
    "OccupancyIdentifier": "address1",
    "PlaceName": "city",
    "StateName": "state",
    "ZipCode": "zip_code",
    "SubaddressType": "address1",
    "SubaddressType": "address1",
    "SubaddressIdentifier": "address1",
}

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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
    addresses = []

    r = session.get("https://f45training.com/find-a-studio/")
    soup = BeautifulSoup(r.text, "html5lib")
    script = str(soup.find(text=re.compile("window.studios")))
    jsondata = json.loads(
        script.split("window.studios = ")[1]
        .split("window.country_name")[0]
        .replace("};", "}")
    )["hits"]

    for i in jsondata:
        location_name = "<MISSING>"
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zipp = "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        if i["country"] == "United States":
            latitude = i["_geoloc"]["lat"]
            longitude = i["_geoloc"]["lng"]
            location_name = i["name"].replace("F45", "").strip()
            address = i["location"]
            try:
                addr_format = usadr.tag(address, tm)
                addr = list(addr_format[0].items())
                street_address = addr[0][1]
            except:
                pass
            try:
                city = address.split(",")[1].strip()
            except:
                pass
            try:
                postal_code = "".join(address.split(",")[2]).strip()
                zipp1 = re.search(r"\d{5}(-\d{4})?$", postal_code)
                zipp = zipp1.group(0)
            except:
                pass

            state = i["state"]
            country_code = "US"
            store_number = i["id"]

        elif i["country"] == "Canada":
            location_name = i["name"].replace("F45", "").strip()
            address = i["location"]
            try:
                street_address = address.split(",")[0].strip()
                city = address.split(",")[1].strip()
                postal_code1 = "".join(address.split(","))
                temp_zipp = re.search(r"[A-Z]\d[A-Z]\s\d[A-Z]\d", postal_code1)
                a = temp_zipp.group(0)
                if len(a) == 7:
                    zipp = a
                else:
                    zipp = "<MISSING>"
            except:
                pass
            try:
                state = i["state"].split("(")[1].replace(")", "")
            except:
                state = "<MISSING>"

            country_code = "CA"
            store_number = i["id"]
            latitude = i["_geoloc"]["lat"]
            longitude = i["_geoloc"]["lng"]
        else:
            continue

        page_url = "https://f45training.com/" + i["slug"]
        location_request = session.get(page_url)
        location_soup = BeautifulSoup(location_request.text, "html5lib")
        if location_request.status_code != 200:
            phone = "<INACCESSIBLE>"
        else:
            try:
                phone = (
                    location_soup.find("a", {"href": re.compile("tel:")})
                    .text.split("/")[0]
                    .split(",")[0]
                    .replace("(JF45)", "")
                )
            except:
                phone = "<INACCESSIBLE>"
                pass

        store = []
        store.append("https://f45training.com/")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<INACCESSIBLE>")
        store.append("F45")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append("<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
