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

    base_link = "https://www.uniqlo.com/us/en/find-stores/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="storeitem")
    locator_domain = "uniqlo.com"

    for item in items:
        location_name = item.a.text.split("-")[0].strip()
        street_address = item.find(class_="streetAddress").text.strip()
        city_line = item.find(class_="addressLocality").text.split(",")
        city = city_line[0]
        state = city_line[1].split()[0]
        zip_code = city_line[1].split()[1]
        country_code = "US"
        location_type = "<MISSING>"

        link = "https://www.uniqlo.com" + item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        store_number = link.split("=")[1].split("&")[0]
        phone = "<MISSING>"

        hours_of_operation = "<INACCESSIBLE>"

        latitude = (
            re.findall(r"lat: Number\([0-9]{2}\.[0-9]+\)", str(base))[0]
            .split("(")[1]
            .split(")")[0]
        )
        longitude = (
            re.findall(r"lng: Number\(-[0-9]{2,3}\.[0-9]+\)", str(base))[0]
            .split("(")[1]
            .split(")")[0]
        )

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
