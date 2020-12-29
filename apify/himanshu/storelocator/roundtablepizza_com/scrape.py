import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }

    base_url = "https://www.roundtablepizza.com/"
    r = session.get(
        "https://ordering.roundtablepizza.com/site/rtp/locations", headers=headers
    )
    soup = BeautifulSoup(r.text, "lxml")

    for dt in soup.find("div", {"class": "coordinatosContainer"}).find_all(
        "div", {"class": "coordinatos"}
    ):
        name = dt["data-name"]
        address = dt["data-address1"]
        city = dt["data-address2"].split(",")[0].strip().split("  ")[0]
        state = dt["data-address2"].split(",")[0].strip().split("  ")[1]
        temp_zip = dt["data-address2"].split(",")[1]
        if len(temp_zip) > 1:
            zip = dt["data-address2"].split(",")[1]
        else:
            zip = "<MISSING>"
        if dt["data-phone"] == "":
            phone = "<MISSING>"
        else:
            phone = dt["data-phone"]
        if len(dt["data-latitude"]) > 1:
            latitude = dt["data-latitude"]
        else:
            latitude = "<MISSING>"
        if len(dt["data-longitude"]) > 1:
            longitude = dt["data-longitude"]
        else:
            longitude = "<MISSING>"
        if len(dt["data-url"]) > 1:
            page_url = dt["data-url"]
        else:
            page_url = "<MISSING>"
        hours_of_operation = "<INACCESIBLE>"

        store = []
        store.append(base_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("Restaurant")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
