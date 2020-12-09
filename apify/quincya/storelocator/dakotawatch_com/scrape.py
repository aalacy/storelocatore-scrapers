import csv
import time

from bs4 import BeautifulSoup

from sgselenium import SgChrome


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

    base_link = (
        "https://findastore.appdevelopergroup.co/embed/27b82c6f4bd86d69ba7d77bdff9eb577"
    )

    driver = SgChrome().chrome()

    driver.get(base_link)
    time.sleep(10)

    base = BeautifulSoup(driver.page_source, "lxml")

    items = base.find_all(class_="fas_list_res_i")

    data = []
    for item in items:
        locator_domain = "dakotawatch.com"
        location_name = item.find(class_="fas_store_name").text.strip()
        raw_data = item.find(class_="fas_address").text.split(",")
        street_address = raw_data[0].strip()
        city = raw_data[1].strip()
        state = raw_data[2].strip()
        zip_code = raw_data[3].strip()
        country_code = "US"
        store_number = item["data-ind"]
        phone = item.find(class_="fas_phone").text.strip()
        location_type = "<MISSING>"
        latitude = item["data-lat"]
        longitude = item["data-lng"]
        hours_of_operation = "<MISSING>"
        link = "<MISSING>"

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
