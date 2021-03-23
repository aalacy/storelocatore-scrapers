import csv
import json

from bs4 import BeautifulSoup
from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )

        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }

    session = SgRequests()
    locator_domain = "https://www.bhotelsandresorts.com"
    r = session.get("https://www.bhotelsandresorts.com/destinations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    country_code = "US"
    store_number = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"

    script_temp = soup.find(id="menu-main").ul
    for script_location in script_temp.find_all("li"):
        location_url = script_location.find("a")["href"]

        r1 = session.get(location_url, headers=headers)
        tree = html.fromstring(r1.text)

        text = "".join(tree.xpath("//script[contains(text(), 'places')]/text()"))
        text = text.split('"places":[')[-1].split("}}")[0] + "}}}"
        address_json = json.loads(text)

        location_name = tree.xpath(
            "//div[contains(@class,'vc_custom_heading')]/h2/text()"
        )[0].strip()
        street_address = address_json["address"].split(",")[0]
        state = address_json["location"]["state"]
        city = address_json["location"]["city"]
        zipp = address_json["location"]["postal_code"]
        if not state:
            city = address_json["address"].split(",")[1].strip()
            state = address_json["address"].split(",")[2].split()[0].strip()
            zipp = address_json["address"].split(",")[2].split()[1].strip()
        latitude = address_json["location"]["lat"]
        longitude = address_json["location"]["lng"]
        phone = address_json["content"]
        if "-" not in phone:
            phone = "<MISSING>"

        store = [
            locator_domain,
            location_url,
            location_name,
            street_address,
            city,
            state,
            zipp,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
