import csv
import time

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgselenium import SgChrome

log = SgLogSetup().get_logger("haggen_com")


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

    base_link = "https://www.haggen.com/find-our-stores/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    driver = SgChrome(user_agent=user_agent).driver()

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    locator_domain = "haggen.com"

    items = base.find_all(class_="crunchyBox")

    for item in items:

        raw_data = list(item.stripped_strings)

        location_name = raw_data[0].strip()
        street_address = raw_data[1].strip()
        city_line = raw_data[2].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = item["id"].split("post-")[1]
        location_type = "<MISSING>"
        phone = raw_data[3].replace("Phone:", "").strip()
        hours_of_operation = "<MISSING>"

        link = item.a["href"]

        log.info(link)

        driver.get(link)
        time.sleep(4)

        base = BeautifulSoup(driver.page_source, "lxml")

        raw_data = list(base.find(class_="contactInfo").stripped_strings)
        for i, row in enumerate(raw_data):
            if "store hours" in row.lower():
                hours_of_operation = raw_data[i + 1]

        raw_gps = driver.find_element_by_xpath(
            "//*[(@title='Open this area in Google Maps (opens a new window)')]"
        ).get_attribute("href")
        latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find(",")].strip()
        longitude = raw_gps[raw_gps.find(",") + 1 : raw_gps.find("&")].strip()

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
