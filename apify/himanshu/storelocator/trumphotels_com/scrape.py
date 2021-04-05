import csv
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgselenium import SgChrome
import json

logger = SgLogSetup().get_logger("trumphotels.com")


def write_output(data):
    with open("data.csv", newline="", mode="w") as output_file:
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    driver = SgChrome().driver()
    base_url = "https://www.trumphotels.com"
    driver.get("https://www.trumphotels.com/")
    soup = BeautifulSoup(driver.page_source, "lxml")

    for country in soup.find("div", {"id": "ourhotels"}).find_all(
        "div", {"class": "filterlist"}
    ):
        for location in country.find_all("a"):
            logger.info(f" scraping: {location}")
            driver.get(base_url + location["href"])
            page_url = base_url + location["href"]
            location_soup = BeautifulSoup(driver.page_source, "html.parser")
            for script in location_soup.find_all(
                "script", {"type": "application/ld+json"}
            ):
                store_data = json.loads(script.string)
                if "address" in store_data:
                    if store_data["address"]["addressCountry"] not in ("USA", "Canada"):
                        continue
                    name = location.text.strip()
                    address = store_data["address"]
                    geo_location = location_soup.find("div", {"class": "map-outer-div"})
                    store = []
                    store.append("https://www.trumphotels.com")
                    store.append(name.replace("®", ""))
                    store.append(address["streetAddress"])
                    store.append(address["addressLocality"].split(",")[0])
                    store.append(
                        address["addressRegion"].strip()
                        if "addressRegion" in address
                        else address["addressLocality"].split(",")[1]
                    )
                    store.append(address["postalCode"])
                    store.append("US" if address["addressCountry"] == "USA" else "CA")
                    store.append("<MISSING>")
                    store.append(
                        store_data["telephone"]
                        if store_data["telephone"]
                        else "<MISSING>"
                    )
                    store.append("<MISSING>")
                    store.append(geo_location["data-latitude"])
                    store.append(geo_location["data-longitude"])
                    store.append("<MISSING>")
                    store.append(page_url)
                    yield store
    driver.quit()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
