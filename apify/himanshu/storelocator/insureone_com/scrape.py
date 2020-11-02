import csv
import json
from bs4 import BeautifulSoup
from sgrequests import SgRequests

MISSING = "<MISSING>"
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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


def get_states():
    response = session.get("https://www.insureone.com/find-an-office/", headers=headers)
    bs4 = BeautifulSoup(response.text, "html.parser")
    options = bs4.select("#state option")
    states = [
        option.attrs.get("value") for option in options if option.attrs.get("value")
    ]
    return states


def get_location_data(url):
    response = session.get(url)
    bs4 = BeautifulSoup(response.text, "html5lib")
    data = bs4.find("script", {"type": "application/ld+json"}).text.strip()
    return json.loads(data)


def format_hours(hours):
    return (
        ",".join(hours)
        .replace("Mo", "MON :")
        .replace("Tu", "TUE :")
        .replace("We", "WED :")
        .replace("Th", "THU :")
        .replace("Fr", "FRI :")
        .replace("Sa", "SAT :")
        .replace("Su", "SUN :")
        .strip()
    ) or MISSING


def fetch_data():
    states = get_states()

    for state in states:
        locator_domain = "insureone.com"
        data = {"search_state": state}
        r = session.post(
            "https://www.insureone.com/locations/", data=data, headers=headers
        )
        soup = BeautifulSoup(r.text, "lxml")
        locations = soup.select(".office-locator-results__title")

        for location in locations:
            location_name = location.getText().replace(": Maps", "")
            page_url = location.find("a").get("href")

            location_data = get_location_data(page_url)

            address = location_data.get("address", {})
            street_address = address.get("streetAddress", MISSING)
            city = address.get("addressLocality", MISSING)
            state = address.get("addressRegion", MISSING)
            postal = address.get("postalCode", MISSING)
            country_code = address.get("addressCountry", MISSING)

            geolocation = location_data.get("geo", {})
            latitude = geolocation.get("latitude", MISSING)
            longitude = geolocation.get("longitude", MISSING)

            phone = location_data.get("telephone").strip()
            location_type = location_data.get("name").strip()
            hours_of_operation = format_hours(location_data.get("openingHours"))
            store_number = MISSING

            store = [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                postal,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
                page_url,
            ]

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
