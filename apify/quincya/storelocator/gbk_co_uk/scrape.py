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

    base_link = "https://gbk.co.uk/find-your-gbk"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    locator_domain = "https://gbk.co.uk"

    js = (
        str(base)
        .replace("&quot;", '"')
        .split('restaurants="')[1]
        .split('"></find-page')[0]
    )
    stores = json.loads(js)

    for store_data in stores:
        link = store_data["permalink"]
        location_name = store_data["title"]
        street_address = store_data["address_lines"][0]["address_line"]
        city = store_data["city"]
        if city in street_address.strip()[-len(city) :]:
            street_address = " ".join(street_address.split(",")[:-1])
        state = store_data["county_region"]
        if not state:
            state = "<MISSING>"
        zip_code = store_data["zip_postal_code"]
        country_code = "GB"
        location_type = "<MISSING>"
        store_number = store_data["restaurant_id"]
        if not store_number:
            store_number = "<MISSING>"
        phone = store_data["telephone_display"]
        if not phone:
            phone = "<MISSING>"
        latitude = store_data["latitude"]
        longitude = store_data["longitude"]

        hours_of_operation = ""
        raw_hours = store_data["opening_hours"]
        for hours in raw_hours:
            day = hours["day"]
            if hours["restaurant_closed"]:
                times = "Closed"
            else:
                opens = hours["opening_time"]
                closes = hours["closing_time"]
                times = opens + "-" + closes
            if opens != "" and closes != "":
                clean_hours = day + " " + times
                hours_of_operation = (hours_of_operation + " " + clean_hours).strip()
        if not hours_of_operation:
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
