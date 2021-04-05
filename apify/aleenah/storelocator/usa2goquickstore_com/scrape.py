import csv
from sgselenium import SgSelenium
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("usa2goquickstore_com")


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

    all = []

    driver.get("https://usa2goquickstore.com/locations/")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    stores = soup.find_all("div", {"class": "fusion-column-content"})

    if len(stores) == 0:
        for i in range(5):
            driver.get("https://usa2goquickstore.com/locations/")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            stores = soup.find_all("div", {"class": "fusion-column-content"})
            if len(stores) != 0:
                break

    for store in stores:
        loc = store.find("h2").text.strip()
        data = (
            store.find_all("div", {"class": "fusion-text"})[1]
            .text.replace("click here for directions", "")
            .strip()
            .split("\n")
        )
        logger.info(data)

        street = data[0].strip()
        try:
            sz = data[1].strip().split(",")
            city = sz[0]
            sz = sz[1].strip().split(" ")
            state = sz[0]
            zip = sz[1]
        except:
            sz = data[1].strip().split(" ")
            zip = sz[-1]
            state = sz[-2]
            city = data[1].replace(zip, "").replace(state, "").strip()

        phone = data[2].replace("t:", "").replace("\xa0", "").strip()

        all.append(
            [
                "https://usa2goquickstore.com",
                loc,
                street,
                city,
                state,
                zip,
                "US",
                "<MISSING>",  # store #
                phone,  # phone
                "<MISSING>",  # type
                "<MISSING>",  # lat
                "<MISSING>",  # long
                "<MISSING>",  # timing
                "https://usa2goquickstore.com/locations/",
            ]
        )
    driver.quit()
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
