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

    base_link = "https://www.billgrays.com/index.cfm?Page=Locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    found = []

    items = base.find_all(class_="part-box")
    locator_domain = "billgrays.com"

    for item in items:

        raw_address = list(item.stripped_strings)

        location_name = raw_address[0]
        street_address = raw_address[1].strip()

        if street_address in found:
            continue
        found.append(street_address)

        city_line = raw_address[2].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        phone = raw_address[3].strip()

        country_code = "US"
        store_number = "<MISSING>"
        if "Abbotts Logo" in str(item):
            location_type = "Abbott's"
        else:
            location_type = "No Abbott's"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        link = item.find(class_="part-box-btn")["href"]
        if "index.cfm?Page" in link:
            link = "https://www.billgrays.com" + link
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            rows = list(base.find(class_="loc-col1 contentnorm").stripped_strings)
            for i, r in enumerate(rows):
                if "hours" in r.lower():
                    hours = " ".join(rows[i + 1:])
                    break

            hours_of_operation = hours.split("Inside")[0].split("Located")[0].strip()

            if "-" not in phone:
                phone = base.find(title="click here to call this location").text

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
