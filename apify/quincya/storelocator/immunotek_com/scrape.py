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

    base_link = "https://www.immunotek.com/locations-2/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    locator_domain = "immunotek.com"

    sections = base.find(
        class_="et_pb_section et_pb_section_3 et_pb_with_background et_section_regular"
    ).find_all("div", recursive=False)
    for section in sections:
        items = section.find_all("div", recursive=False)
        for item in items:
            if not list(item.stripped_strings):
                continue
            if "coming-soon" in str(item):
                continue

            location_name = "ImmunoTek " + item.p.text.split(",")[0].strip()

            raw_address = list(item.find_all("p")[2].stripped_strings)
            street_address = raw_address[0]
            city = raw_address[1].split(",")[0]
            state = raw_address[1].split(",")[1].split()[0]
            zip_code = raw_address[1].split(",")[1].split()[1]
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            phone = item.find_all("p")[1].text

            map_str = item.find_all("p")[2].a["href"]
            try:
                geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[
                    0
                ].split(",")
                latitude = geo[0]
                longitude = geo[1]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            hours_of_operation = " ".join(
                list(item.find_all("p")[3].stripped_strings)
            ).strip()

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
