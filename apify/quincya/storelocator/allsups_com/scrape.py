import csv

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

    base_link = "https://allsups.com/allsups-locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="white-popup mfp-hide hidden-collapse")
    locator_domain = "allsups.com"

    for item in items:

        location_name = item.h3.text.strip()
        raw_address = list(item.address.stripped_strings)
        street_address = raw_address[0].strip()
        city = raw_address[-1].split(",")[0].strip()
        state = raw_address[-1].split(",")[1].split()[0].strip()
        zip_code = raw_address[-1].split()[-1].strip()

        if street_address == "1608 S. Main St":
            zip_code = "88260"
        if street_address == "913 West 8th Street":
            zip_code = "76437"

        country_code = "US"
        store_number = location_name.split("#")[-1].strip()

        try:
            raw_types = item.find(class_="list-inline").find_all("li")
            location_type = ""
            for raw_type in raw_types:
                location_type = (location_type + ", " + raw_type.img["title"]).strip()
            location_type = location_type[1:].strip()
        except:
            location_type = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = " ".join(
            list(item.find(class_="list-unstyled").stripped_strings)
        ).replace(
            "Sunday: Monday: Tuesday: Wednesday: Thursday: Friday: Saturday:",
            "<MISSING>",
        )

        latitude = (
            item.find(class_="map-canvas-var")["center"].split(",")[0][1:].strip()
        )
        longitude = (
            item.find(class_="map-canvas-var")["center"].split(",")[1][:-1].strip()
        )

        data.append(
            [
                locator_domain,
                base_link,
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
