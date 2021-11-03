import csv
import re
import time
from sglogging import SgLogSetup
from sgselenium import SgSelenium

logger = SgLogSetup().get_logger("joescrabshack_com")


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


driver = SgSelenium().chrome()


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []

    driver.get("https://www.joescrabshack.com/store-locator/")
    time.sleep(5)
    divs = driver.find_elements_by_class_name("locationListItem")
    logger.info(len(divs))
    for div in divs:
        a = div.find_element_by_tag_name("h3").find_element_by_tag_name("a")
        locs.append(a.text)
        sa = div.find_elements_by_tag_name("a")
        a = sa[1]
        coord = a.get_attribute("href")
        if "query_place_id=" in coord:
            lat.append(re.findall(r"query=(-?[\d\.]*)", coord)[0])
            long.append(re.findall(r"query=[-?\d\.]*,([-?\d\.]*)", coord)[0])
        else:
            lat.append("<MISSING>")
            long.append("<MISSING>")
        addr = a.text.strip().split(",")
        sz = addr[-1].strip().split(" ")
        states.append(sz[0])
        zips.append(sz[1])
        del addr[-1]
        cities.append(addr[-1])
        del addr[-1]
        street.append(", ".join(addr))
        a = sa[2]
        phones.append(a.text.strip())
        tim = div.find_element_by_class_name("locationListItemHours").text
        tim = ", ".join(re.findall(".*PM", tim, re.DOTALL)[0].split("\n"))
        timing.append(tim)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.joescrabshack.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append("https://www.joescrabshack.com/store-locator/")  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
