import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

from util import Util  # noqa: I900

myutil = Util()


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
    locator_domain = "https://www.elchico.com/locations/"
    r = session.get(locator_domain)
    soup = bs(r.text, "lxml")
    locations = soup.select(".all-loc-1 .single-location")
    data = []
    for location in locations:
        page_url = location.a["href"]
        location_name = location.a.text.strip()
        address = location.select_one(".location-address").text.split("\r\n")
        country_code = "US"
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zip = "<MISSING>"
        if address[-1].split(",")[1].strip() == "UAE":
            continue
        else:
            zip = address[-1].split(",")[1].strip().split(" ")[1]
            state = address[-1].split(",")[1].strip().split(" ")[0]
            city = address[-1].split(",")[0]
            street_address = " ".join(address[:-1])
        phone = myutil._valid(location.select_one(".tel a").text)
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = ""
        hours = [_ for _ in location.select_one(".my-hours p").stripped_strings]
        for x, hour in enumerate(hours):
            if x % 2 == 0:
                hours_of_operation += hour + ":"
            else:
                hours_of_operation += hour + ";"

        hours_of_operation = myutil._valid(hours_of_operation)
        _item = [
            locator_domain,
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
        data.append(_item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
