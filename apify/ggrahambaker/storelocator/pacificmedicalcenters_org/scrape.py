import csv
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def addy_ext(addy):
    addy = addy.split(",")
    if len(addy) == 1:
        addy = addy[0].split(" ")
        city = addy[0]
        state = addy[1]
        zip_code = addy[2]
    else:
        city = addy[0]
        state_zip = addy[1].strip().split(" ")
        state = state_zip[0]
        zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data():
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    locator_domain = "https://www.pacificmedicalcenters.org/"
    ext = "where-we-are/"

    r = session.get(locator_domain + ext, headers=headers)

    soup = BeautifulSoup(r.content, "html.parser")

    menu = soup.find("li", {"id": "menu-item-503"})

    locs = menu.find_all("li")
    all_store_data = []
    for loc in locs:
        page_url = loc.a["href"]
        r = session.get(page_url, headers=headers)

        soup = BeautifulSoup(r.content, "html.parser")

        location_name = soup.h1.text
        addy = list(soup.find(class_="circles-text").stripped_strings)[1:-1]
        street_address = addy[0].replace("\t", " ").strip()
        street_address = (re.sub(" +", " ", street_address)).strip()
        city, state, zip_code = addy_ext(addy[1].strip())

        lat = re.findall(r'lat":"[0-9]{2}\.[0-9]+', str(soup))[0].split(":")[1][1:]
        longit = re.findall(r'lng":"-[0-9]{2,3}\.[0-9]+', str(soup))[0].split(":")[1][
            1:
        ]

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        try:
            phone_number = re.findall(
                r"[(\d)]{5} [\d]{3}-[\d]{4}", str(soup.find(class_="page-content"))
            )[0]
        except:
            phone_number = "<MISSING>"

        rows = list(soup.find(class_="page-content").stripped_strings)
        hours = ""
        for i, row in enumerate(rows):
            if "CLINIC HOURS" in row.upper():
                for y in range(4):
                    hour = rows[i + 1 + y]
                    if (
                        "day" in hour.lower()
                        or "appointment" in hour.lower()
                        or "pm" in hour.lower()
                    ):
                        hours = (hours + " " + hour).strip()
        if not hours:
            hours = "<MISSING>"

        store_data = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            longit,
            hours,
            page_url,
        ]

        all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
