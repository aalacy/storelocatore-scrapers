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

    base_link = "https://www.lecreuset.co.uk/en_GB/stores/cop004.html#UK"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"

    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)

    base = BeautifulSoup(driver.page_source, "lxml")

    data = []
    locator_domain = "lecreuset.co.uk"

    items = base.find(id="UK").find_all(class_="mb-3")

    for item in items:

        raw_data = list(item.stripped_strings)
        if len(raw_data) == 1:
            continue
        if "IRELAND" in item.text.upper():
            break

        location_name = raw_data[0].strip()
        street_address = (
            " ".join(raw_data[1:-4])
            .replace("Le Creuset House", "")
            .replace("St Albans", "")
            .strip()
        )
        if not street_address:
            street_address = raw_data[1].strip()
        city = location_name.split("CREUSET")[-1].strip()
        state = raw_data[-4].strip()
        if "london" in location_name.lower():
            state = "London"
            if "•" in location_name:
                city = location_name.split("•")[1].strip()
        zip_code = raw_data[-3].strip()
        if "," in zip_code:
            state = zip_code.split(",")[0].strip()
            zip_code = " ".join(zip_code.split(",")[1:]).strip()
        if city == state:
            state = "<MISSING>"
        country_code = "GB"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = raw_data[-2].strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
