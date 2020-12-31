import csv

from bs4 import BeautifulSoup

from sgselenium import SgChrome


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

    base_link = "https://www.northerntool.com/stores/stores.xml"

    driver = SgChrome().chrome()

    driver.get(base_link)

    base = BeautifulSoup(driver.page_source, "lxml")

    store_data = base.find_all("row")

    data = []
    locator_domain = "northerntool.com"

    for store in store_data:
        location_name = store.h1.text
        street_address = store.address.text.replace("<br>", " ").strip()
        city = store.city.text.strip()
        state = store.state.text.strip()
        zip_code = store.zipcode.text.strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = store.phone.text.strip()
        hours_of_operation = store.storehours.text.replace("<br/>", " ")
        latitude = store.coordinates.text.split(",")[0].strip()
        longitude = store.coordinates.text.split(",")[1].strip()
        link = "https://www.northerntool.com/stores/" + store.url.text

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

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
