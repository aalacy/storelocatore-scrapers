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

    base_link = "https://www.kedplasma.us/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="city_mobile")
    locator_domain = "kedplasma.us"

    for item in items:
        if "OPENING" in item.text.upper():
            continue
        location_name = item.b.text.strip()
        street_address = item.a.text.split(",")[1].strip()[2:]
        city = item.b.text.split(",")[0].strip().split("-")[0]
        state = item.b.text.split(",")[1].strip()
        zip_code = item.a.text.split(",")[-2].split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = item.a.text.split(",")[-1]

        link = item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        hours_of_operation = (
            " ".join(
                (
                    list(base.find(class_="plasma-center-contact-us").stripped_strings)[
                        :-1
                    ]
                )
            )
            .replace("\xa0", " ")
            .replace("Opening hours:", "")
            .split("KEDPLASMA")[0]
            .split("Se hab")[0]
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.encode("ascii", "replace").decode().replace("?", "-")
        )
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

        all_scripts = base.find_all("script")
        for script in all_scripts:
            if "myLatlng" in str(script):
                script = str(script)
                geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", script)[
                    0
                ].split(",")
                latitude = geo[0]
                longitude = geo[1]
                break

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
