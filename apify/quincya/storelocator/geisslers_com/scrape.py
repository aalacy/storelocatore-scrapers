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

    base_link = "https://www.geisslers.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    locator_domain = "geisslers.com"

    rows = base.find_all(class_="col-sm-4 cmz_agileinfo_portfolio_grid")

    for row in rows:
        items = row.find_all("div", recursive=False)
        for item in items:
            if not item.h4:
                continue
            location_name = item.h4.text.strip()
            raw_data = list(item.stripped_strings)[2:-2]
            street_address = raw_data[0]
            city_line = raw_data[1].split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"

            try:
                phone = re.findall(r"[(\d)]{5} [\d]{3}-[\d]{4}", str(item))[0]
            except:
                phone = "<MISSING>"

            hours = " ".join(raw_data[10:])
            hours = (re.sub(" +", " ", hours)).strip()
            hours_of_operation = (
                hours[hours.find("Mon") : hours.find("pm") + 2] + " " + raw_data[11]
            )
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
