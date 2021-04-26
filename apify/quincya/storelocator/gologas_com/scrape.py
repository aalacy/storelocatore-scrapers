import csv
import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    base_link = "http://www.gologas.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find(id="x-google-map-1").find_all(class_="x-google-map-marker")
    locator_domain = "http://www.gologas.com/"

    for item in items:
        loc = json.loads(item["data-x-params"])

        raw_address = raw_address = loc["markerInfo"].split("|")[1].split(",")
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[2].strip()
        try:
            zip_code = re.findall(r"[0-9]{5}", loc["markerInfo"])[0]
        except:
            zip_code = "<MISSING>"

        country_code = "US"
        store_number = "<MISSING>"
        icon = loc["image"]
        if "savemarker" in icon:
            location_type = "Save"
        elif "allstarmarker" in icon:
            location_type = "AllStar"
        elif "golomarker" in icon:
            location_type = "GoLo"
        else:
            location_type = "<MISSING>"

        location_name = location_type + " " + city
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = loc["lat"]
        longitude = loc["lng"]

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
