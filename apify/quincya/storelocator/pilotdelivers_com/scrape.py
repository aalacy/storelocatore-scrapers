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

    base_links = [
        "https://www.pilotdelivers.com/global-network/domestic/",
        "https://www.pilotdelivers.com/global-network/international/",
    ]

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    data = []

    locator_domain = "pilotdelivers.com"

    for base_link in base_links:

        session = SgRequests()
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        items = base.find_all(class_="locations-link")

        for item in items:
            location_name = item.find(class_="station-title").text
            street_address = item.find_all("h6")[1].text.replace("66265", "").strip()
            city_line = item.find_all("h6")[2].text.split(",")
            if "domestic" in base_link:
                city = city_line[0].strip()
                state = city_line[-1].strip().split()[0].strip()
                zip_code = city_line[-1].strip().split()[1].strip()
                country_code = "US"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
            else:
                country_code = location_name.split(",")[1].strip()
                city = location_name.split(",")[0].strip()
                if country_code == "Canada":
                    city = city_line[0].strip()
                    state = city_line[-1].strip().split()[0].strip()
                    zip_code = " ".join(city_line[-1].strip().split()[1:]).strip()
                else:
                    if len(city_line) == 3:
                        city = city_line[0].strip()
                        state = city_line[1].strip()
                        zip_code = city_line[-1].strip()
                    elif len(city_line) == 2:
                        state = "<MISSING>"
                        zip_code = city_line[-1].strip()
                        if city != city_line[0].strip():
                            street_address = street_address + " " + city_line[0].strip()
            street_address = (re.sub(" +", " ", street_address)).strip()
            if street_address[-1:] == ",":
                street_address = street_address[:-1]

            phone = (
                item.find(class_="station-contact")
                .a.text.replace("Main Phone:", "")
                .strip()
            )
            hours_of_operation = "<MISSING>"
            latitude = "<INACCESSIBLE>"
            longitude = "<INACCESSIBLE>"
            link = item["data-href"]
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
