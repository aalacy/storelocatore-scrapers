import csv


from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("safeway_ca")


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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []

    base_url = "https://www.safeway.ca/"

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    }

    location_url = "https://www.safeway.ca/find-a-store/"

    r = session.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("div", {"class": "store-result"})
    for location in data:
        store_number = location["data-id"]
        latitude = location["data-lat"]
        longitude = location["data-lng"]
        city = location["data-city"].title()
        state = location["data-province"].upper()
        zipp = location["data-postal-code"].upper()
        location_name = location.find("span", {"class": "name"}).text
        street_address = location.find(
            "span", {"class": "location_address_address_1"}
        ).text
        phone = location.find("span", {"class": "phone"}).text
        page_url = location.find("a")["href"]
        logger.info(page_url)
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        hours = " ".join(
            list(
                soup1.find("table", {"class": "holiday_hours_tbl"})
                .find("tbody")
                .stripped_strings
            )
        )
        location_type = "<MISSING>"

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("CA")
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
