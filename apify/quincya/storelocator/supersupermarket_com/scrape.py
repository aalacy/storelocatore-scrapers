import csv
import ssl

from bs4 import BeautifulSoup

from sgselenium import SgChrome

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


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

    base_link = "http://supersupermarket.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)
    base = BeautifulSoup(driver.page_source, "lxml")

    items = base.find_all(class_="jss6")

    data = []
    for item in items:
        locator_domain = "supersupermarket.com"
        country_code = "US"
        store_number = "<MISSING>"
        phone = item.h6.text.strip()
        location_type = "<MISSING>"
        hours_of_operation = " ".join(list(item.stripped_strings)[3:])

        link = (
            "http://supersupermarket.com/"
            + item["style"].split("media/")[1].split(".")[0]
        )

        raw_line = item.h5.text.strip()
        if "," in raw_line:
            raw_address = raw_line.split(",")
        else:
            raw_address = raw_line.split()
        street_address = " ".join(raw_address[:-2])
        city = raw_address[-2].strip()
        state = raw_address[-1].strip().upper()

        if "30 Main Street" in street_address:
            zip_code = "07505"
        elif "53 South Jefferson" in street_address:
            zip_code = "07050"
        elif "1007 Memorial Drive" in street_address:
            zip_code = "07712"
        else:
            zip_code = "<INACCESSIBLE>"

        location_name = "Super Supermarket " + city

        driver.get(link)
        base = BeautifulSoup(driver.page_source, "lxml")

        raw_gps = base.iframe["src"]
        start_point = raw_gps.find("2d") + 2
        longitude = raw_gps[start_point : raw_gps.find("!", start_point)]
        long_start = raw_gps.find("!", start_point) + 3
        latitude = raw_gps[long_start : raw_gps.find("!", long_start)]
        try:
            int(latitude[4:8])
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
