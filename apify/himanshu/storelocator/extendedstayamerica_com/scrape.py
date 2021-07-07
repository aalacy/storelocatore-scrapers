import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from lxml import html


session = SgRequests()
session.max_redirects = 1000
import json


# +1.912.692.0076
def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36"
    }
    addresses = []
    base_url = "https://www.extendedstayamerica.com"
    session = SgRequests()
    r = session.get("https://www.extendedstayamerica.com/hotels", headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    jd = (
        str(soup)
        .split("window.esa.hotelsData = ")[1]
        .split("</script>")[0]
        .replace("}];", "}]")
    )

    json_data = json.loads(jd)

    for value in json_data:
        a = value["address"]

        location_name = value["title"]
        street_address = a["street"]
        city = a["city"]
        state = a["region"]
        zipp = a["postalCode"]
        country_code = "US"
        store_number = value["siteId"]

        location_type = "<MISSING>"
        latitude = value["latitude"]
        longitude = value["longitude"]
        hours_of_operation = "Open 24 hours a day, seven days a week"
        page_url = "https://www.extendedstayamerica.com" + value["urlMap"]

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        try:
            phone = (
                "".join(
                    tree.xpath("//script[contains(text(), " "telephone" ")]/text()")
                )
                .split('"telephone": "')[1]
                .split('"')[0]
                .strip()
            )
        except:
            phone = "<MISSING>"

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
