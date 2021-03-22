import csv
import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_link = "https://www.sbe.com/restaurants/katsuya#locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")
    data = []

    items = base.find(class_="cards__row cards__row--default").find_all(
        "a", class_="card__link card__link--primary"
    )
    locator_domain = "sbe.com"

    for item in items:
        link = item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        script = base.find(class_="region region-content").script.contents[0]
        store = json.loads(script)

        location_name = store["name"]
        country_code = store["address"]["addressCountry"]
        street_address = store["address"]["streetAddress"].split(", Los ")[0].strip()
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store["telephone"]
        hours_of_operation = (
            " ".join(list(base.find(class_="card__hours-details").stripped_strings))
            .replace("Hours", "")
            .split("We apol")[0]
            .split("Dragon")[0]
            .strip()
        )
        latitude = re.findall(r'lat":"[0-9]{2}\.[0-9]+', str(base))[0].split(":")[1][1:]
        longitude = re.findall(r'lng":"-[0-9]{2,3}\.[0-9]+', str(base))[0].split(":")[
            1
        ][1:]

        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
