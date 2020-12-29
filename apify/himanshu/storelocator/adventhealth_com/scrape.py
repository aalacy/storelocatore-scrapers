import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests

base_url = "http://adventhealth.com/"
session = SgRequests()


def fetch_data():
    address = []
    url = "https://www.adventhealth.com/find-a-location?facility=&name=&geolocation_geocoder_google_geocoding_api=&geolocation_geocoder_google_geocoding_api_state=1&latlng%5Bdistance%5D%5Bfrom%5D=-&latlng%5Bvalue%5D=&latlng%5Bcity%5D=&latlng%5Bstate%5D=&latlng%5Bprecision%5D=&service=&page="
    for i in range(109):
        page = session.get(url + str(i))
        soup = BeautifulSoup(page.text, "lxml")
        rows = soup.find_all("li", {"class": "facility-search-block__item"})
        for r in rows:
            try:
                name = (
                    r.find("span", {"class": "location-block__name-link-text"})
                    .get_text()
                    .strip()
                )
                link = r.find(
                    "a",
                    {"class": "location-block__name-link u-text--fw-300 notranslate"},
                ).get("href")
                page_url = base_url + link
            except Exception:
                name = r.find_all("h3")[0].get_text().strip()
                page_url = "<MISSING>"

            try:
                phone = (
                    r.find("a", {"class": "telephone"})
                    .get_text()
                    .strip()
                    .split()[-1][2:]
                )
            except Exception:
                phone = "<MISSING>"

            street = r.find("span", {"property": "streetAddress"}).get_text().strip()
            city = r.find("span", {"property": "addressLocality"}).get_text().strip()
            state = r.find("span", {"property": "addressRegion"}).get_text().strip()
            pin = r.find("span", {"property": "postalCode"}).get_text().strip()
            if len(pin) == 5:
                country_code = "US"
            else:
                country_code = "CA"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = "<INACCESIBLE>"
            lati = r.find("a", {"class": "address notranslate google-maps-link"}).get(
                "data-lat"
            )
            longi = r.find("a", {"class": "address notranslate google-maps-link"}).get(
                "data-lng"
            )

            locations = []
            locations.append(base_url)
            locations.append(name)
            locations.append(street)
            locations.append(city)
            locations.append(state)
            locations.append(pin)
            locations.append(country_code)
            locations.append(store_number)
            locations.append(phone)
            locations.append(location_type)
            locations.append(lati)
            locations.append(longi)
            locations.append(hours_of_operation)
            locations.append(page_url)
            if locations[2] in address:
                continue
            address.append(locations[2])
            yield locations


def load_data(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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


def scrape():
    data = fetch_data()
    load_data(data)


scrape()
