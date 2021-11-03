import csv
import json

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

    base_link = "https://www.newyorkfries.com/locations-new"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    locator_domain = "newyorkfries.com"

    items = base.find_all(role="gridcell")

    for item in items:

        raw_data = list(item.stripped_strings)

        location_name = raw_data[0].strip()
        location_type = raw_data[1].strip()
        city = raw_data[2].strip()
        state = raw_data[3].strip()

        link = item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            street_address = base.find(class_="font_7").text.strip()
        except:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            street_address = base.find(class_="font_7").text.strip()

        try:
            raw_address = json.loads(base.find(id="wix-warmup-data").contents[0])[
                "platform"
            ]["ssrPropsUpdates"][0]["comp-kgkycyag"]["mapData"]["locations"][0]
            zip_code = raw_address["address"].split(",")[-2].strip()[2:].strip()
            if len(street_address) < 5:
                street_address = raw_address["address"]
            latitude = raw_address["latitude"]
            longitude = raw_address["longitude"]
        except:
            zip_code = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if not zip_code:
            zip_code = "<MISSING>"

        street_address = street_address.split(", Cambridge")[0].strip()
        if len(street_address) < 5:
            street_address = "<MISSING>"

        country_code = "CA"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
