import csv
import re

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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.hearinglife.com/webservices/centerlocator.svc/GetCenters/%7B28DE63F1-7F3B-4A11-B81E-114D3D91D052%7D/null/null/en-us/"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["Centers"]

    data = []
    locator_domain = "hearinglife.com"

    for store in stores:
        location_name = BeautifulSoup(store["Title"], "lxml").text.strip()
        street_address = (
            BeautifulSoup(store["Address"], "lxml").text.split("(")[0].strip()
        )

        digit = re.search(r"\d", street_address).start(0)
        if digit != 0:
            street_address = street_address[digit:]

        if street_address[-1:] == ",":
            street_address = street_address[:-1]

        city = store["City"]
        state = store["Region"]
        zip_code = store["PostalCode"]
        if len(zip_code) == 4:
            zip_code = "0" + zip_code
        country_code = "US"
        location_type = "<MISSING>"
        phone = store["Phonenumber"].strip()
        hours_of_operation = ""
        raw_hours = store["OpeningDayHours"]
        for raw_hour in raw_hours:
            hours_of_operation = (
                hours_of_operation
                + " "
                + raw_hour["Day"]
                + " "
                + raw_hour["OpeningHours"]
            ).strip()
        latitude = store["Latitude"]
        longitude = store["Longitude"]
        store_number = store["Id"]
        link = "https://www.hearinglife.com/find-hearing-aid-center"

        # Store data
        data.append(
            [
                locator_domain,
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
                link,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
