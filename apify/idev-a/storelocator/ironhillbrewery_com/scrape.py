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


def _headers():
    return {
        "accept": "application/xml, text/xml, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9,ko;q=0.8",
        "referer": "https://www.ironhillbrewery.com/beerfinder?_ga=2.108452930.1536151032.1612390091-1792985983.1612390091",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    }


def fetch_data():
    data = []

    locator_domain = "https://ironhillbrewery.com/"
    base_url = "https://www.ironhillbrewery.com/data/locations-bf.xml?origLat=39.9496103&origLng=-75.15028210000003&origAddress=526%20Market%20St%2C%20Philadelphia%2C%20PA%2019106%2C%20USA&formattedAddress=&boundsNorthEast=&boundsSouthWest="
    r = session.get(base_url, headers=_headers())
    soup = bs(r.text.strip(), "lxml")
    locations = soup.select("marker")
    for location in locations:
        page_url = "<MISSING>"
        location_name = location["name"]
        store_number = "<MISSING>"
        street_address = (
            f'{location["address"]} {myutil._valid1(location.get("address2", ""))}'
        )
        city = location["city"]
        state = location["state"]
        zip = location["postal"]
        country_code = "US"
        phone = "<MISSING>"
        location_type = location["category"]
        latitude = location["lat"]
        longitude = location["lng"]
        hours_of_operation = "<MISSING>"

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

        myutil._check_duplicate_by_loc(data, _item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
