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

    base_link = "https://c2b-services.bmw.com/c2b-localsearch/services/cache/v4/ShowAll?country=us&category=BD&clientid=UX_NICCE_FORM_DLO"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = base.text.split('"data":')[1].split(',"count"')[0]

    items = json.loads(js)["pois"]

    data = []

    locator_domain = "bmwmotorcycles.com"

    for item in items:
        location_name = item["name"].strip()
        street_address = (
            item["street"].replace("12401Memorial", "12401 Memorial").strip()
        )
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city = item["city"].split(",")[0].strip()
        try:
            state = item["state"].split("/")[0].strip()
        except:
            if city == "Indianapolis":
                state = "IN"
        zip_code = item["postalCode"].strip()
        country_code = item["countryCode"].strip()
        store_number = item["attributes"]["agDealerCode"].split(",")[0].strip()
        location_type = "<MISSING>"
        phone = item["attributes"]["phone"].strip()
        hours_of_operation = "<MISSING>"
        latitude = item["lat"]
        longitude = item["lng"]
        link = item["attributes"]["homepage"].strip()
        if not link:
            link = "<MISSING>"

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
