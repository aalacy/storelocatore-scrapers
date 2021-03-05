import csv

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

    base_link = "https://www.cookiedelivery.com/locations-deliveries.aspx?tab=3"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="col-xs-6 col-sm-4 store-location")

    data = []
    locator_domain = "cookiedelivery.com"

    for item in items:

        if "opens" in str(item).lower() or "opening" in str(item).lower():
            continue
        location_name = item.h6.text.strip()

        raw_address = list(item.p.stripped_strings)

        street_address = raw_address[-3].strip()
        city_line = raw_address[-2].strip().replace("Cypress TX", "Cypress, TX")
        city = city_line.split(",")[0].strip()
        state = city_line.split(",")[1][:-6].strip()
        zip_code = city_line.split(",")[1][-6:].strip()

        if city == "Prosper TX":
            city = "Prosper"
            state = "TX"

        country_code = "US"
        store_number = "<MISSING>"
        phone = raw_address[-1].strip()
        location_type = "<MISSING>"
        hours_of_operation = "<INACCESSIBLE>"
        raw_gps = item.a["href"]
        latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find(",")].strip()
        longitude = raw_gps[raw_gps.find(",") + 1 :].strip()

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
