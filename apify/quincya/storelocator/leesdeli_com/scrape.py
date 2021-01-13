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

    base_link = "https://www.leesdeli.com/location"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all("div", attrs={"data-testid": "mesh-container-content"})[
        2
    ].find_all("div", attrs={"data-testid": "mesh-container-content"})
    locator_domain = "leesdeli.com"

    for item in items:

        location_name = item.h5.text.replace("\xa0", " ").strip()
        if "Menlo" in location_name:
            continue
        street_address = location_name.split("@")[0].strip()
        city_line = city_line = item.p.text.split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        if "Temporar" in item.text:
            location_type = "Temporarily Closed"
        phone = item.find_all("p")[1].text.strip()
        hours_of_operation = ""
        raw_hours = item.find_all("p")[2:]
        for hour in raw_hours:
            hours_of_operation = (
                hours_of_operation + " " + hour.text.replace("\xa0", " ")
            ).strip()
        hours_of_operation = hours_of_operation.split("*")[0].strip()
        latitude = "<INACCESSIBLE>"
        longitude = "<INACCESSIBLE>"

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
