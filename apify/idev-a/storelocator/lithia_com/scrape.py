import csv
from bs4 import BeautifulSoup as bs

from sgrequests import SgRequests

session = SgRequests()


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
    base_url = "https://www.lithia.com"
    r = session.get("https://www.lithia.com/locations/service-locations.htm")
    soup = bs(r.text, "lxml")
    store_list = soup.select("li.info-window")
    data = []
    for s in store_list:
        page_url = "https://www.lithia.com/locations/service-locations.htm"
        location_name = s.select_one("span.org").string
        location_name = location_name.replace("\n", "")
        try:
            street_address = s.select_one("span.street-address").string
            city = s.select_one("span.locality").string
            zip = s.select_one("span.postal-code").string
        except:
            street_address = "<MISSING>"
            city = "<MISSING>"
            zip = "<MISSING>"

        state = s.select_one("span.region").string
        latitude = s.select_one("span.latitude").string
        longitude = s.select_one("span.longitude").string
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        location_type = "<MISSING>"

        data.append(
            [
                base_url,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
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


if __name__ == "__main__":
    scrape()
