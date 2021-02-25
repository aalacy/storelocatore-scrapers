import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    r = session.get("https://f45training.com/find-a-studio/").text
    soup = BeautifulSoup(r, "html5lib")
    script = str(soup.find(text=re.compile("window.studios")))
    jsondata = json.loads(
        script.split("window.studios = ")[1]
        .split("window.country_name")[0]
        .replace("};", "}")
    )["hits"]

    for i in jsondata:
        location_name = "<MISSING>"
        street_address = "<INACCESSIBLE>"
        city = "<INACCESSIBLE>"
        state = "<INACCESSIBLE>"
        zip = "<INACCESSIBLE>"
        country_code = "<INACCESSIBLE>"
        store_number = "<INACCESSIBLE>"
        phone = "<INACCESSIBLE>"
        latitude = "<INACCESSIBLE>"
        longitude = "<INACCESSIBLE>"
        if i["country"] == "United States":
            location_name = i["name"]
            address = i["location"]
            try:
                street_address = address.split(",")[0].strip()
                city = address.split(",")[1].strip()
                zip = address.split(",")[2].strip().split(" ")[1]
            except:
                pass
            state = i["state"]
            country_code = "US"
            store_number = i["id"]
            latitude = i["_geoloc"]["lat"]
            longitude = i["_geoloc"]["lng"]
        elif i["country"] == "Canada":
            location_name = i["name"]
            address = i["location"]
            try:
                street_address = address.split(",")[0].strip()
                city = address.split(",")[1].strip()
                zip = address.split(",")[2].strip().split(" ")[1]
            except:
                pass
            state = i["state"]
            country_code = "CA"
            store_number = i["id"]
            latitude = i["_geoloc"]["lat"]
            longitude = i["_geoloc"]["lng"]
        else:
            continue

        page_url = "https://f45training.com/" + i["slug"]
        location_request = session.get(page_url)
        location_soup = BeautifulSoup(location_request.text, "html5lib")
        if location_soup.find("a", {"href": re.compile("tel:")}) is None:
            phone = "<MISSING>"
        else:
            phone = (
                location_soup.find("a", {"href": re.compile("tel:")})
                .text.split("/")[0]
                .split(",")[0]
                .replace("(JF45)", "")
            )

        store = []
        store.append("https://f45training.com/")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("f45")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append("<MISSING>")
        store.append(page_url if page_url else "<MISSING>")

        if store[2] in addresses:
            continue
        addresses.append(store[2])
        store = [
            str(x).encode("ascii", "ignore").decode("ascii").strip()
            if x
            else "<MISSING>"
            for x in store
        ]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
