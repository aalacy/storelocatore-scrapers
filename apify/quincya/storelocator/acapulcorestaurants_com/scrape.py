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

    base_link = "https://www.acapulcorestaurants.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="location")

    data = []

    locator_domain = "acapulcorestaurants.com"

    for item in items:

        link = item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = item.h2.text.strip()

        raw_address = list(base.find(class_="address").stripped_strings)
        street_address = raw_address[0].strip()
        city = raw_address[1].strip().split(",")[0].strip()
        state = raw_address[1].strip().split(",")[1].strip().split()[0]
        zip_code = "<MISSING>"
        country_code = "US"
        store_number = item["data-location-id"]
        location_type = "<MISSING>"
        phone = base.find(class_="location-contact").a.text
        latitude = item["data-lat"]
        longitude = item["data-lng"]
        hours_of_operation = " ".join(list(base.find(class_="hours").stripped_strings))
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
