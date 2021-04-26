import csv
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

    base_link = "https://www.kumandgo.com/location-sitemap.xml"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all("loc")
    locator_domain = "kumandgo.com"

    for item in items:

        link = item.text
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        raw_data = base.find(id="kng-map")

        location_name = base.h1.text.strip()
        street_address = raw_data["data-address"].strip()
        if not street_address:
            continue
        city = raw_data["data-city"].strip()
        state = raw_data["data-state"].strip()
        zip_code = raw_data["data-zip"].strip()
        if zip_code == "72713":
            zip_code = "72712"
        country_code = "US"
        store_number = link.split("/")[-2]
        phone = raw_data["data-phone"].strip()

        location_type = (
            base.find(class_="no-decoration feature-icons")
            .text.strip()
            .replace("\n\n\n\n\n", ",")
            .strip()
        )
        location_type = (re.sub(" +", " ", location_type)).replace(" , ", ",").strip()

        try:
            hours_of_operation = base.find(class_="hours-24").text.strip()
        except:
            raw_hours = (
                str(base.find(class_="hours")).replace("<br/>", " ").strip()[:-6]
            )
            raw_hours = raw_hours[raw_hours.rfind(">") + 1 :].strip()
            hours_of_operation = (re.sub(" +", " ", raw_hours)).strip()

        latitude = raw_data["data-latitude"].strip()
        longitude = raw_data["data-longitude"].strip()

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
