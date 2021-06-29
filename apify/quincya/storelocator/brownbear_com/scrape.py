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

    base_link = "https://www.brownbear.com/api/v1/locations?radius=5"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    data = []
    locator_domain = "brownbear.com"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["data"]

    for store in stores:
        location_name = store["title"].strip()
        if "Enterprises" in location_name:
            continue
        link = store["url"]
        street_address = store["address_line_1"].strip()
        city_line = store["address_line_2"].split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = store["id"]
        phone = store["phone"]
        latitude = store["lat"]
        longitude = store["lng"]
        location_type = "Open"
        if store["temporarily_closed"]:
            location_type = "Temporarily Closed"

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            hours_of_operation = (
                " ".join(
                    list(base.find(class_="location-hours__list").stripped_strings)
                )
                .replace("Temporarily Closed", "")
                .strip()
            )
        except:
            hours_of_operation = "<MISSING>"

        # Store data
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
