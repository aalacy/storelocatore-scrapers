from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
from sgselenium import SgChrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


def para(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    son = session.get("https://www.merrymaids.com" + url, headers=headers)
    soup = BeautifulSoup(son.text, "lxml")
    k = {}
    try:
        k["StoreDetailsPageUrl"] = url
    except:
        k["StoreDetailsPageUrl"] = "<MISSING>"
    try:
        k["Landmark"] = soup.find(
            "section",
            {
                "id": "LocalFooter",
                "class": "footer",
                "itemtype": "http://schema.org/ProfessionalService",
            },
        ).find("meta", {"itemprop": "name", "content": True})["content"]
    except:
        k["Landmark"] = "<MISSING>"
    try:
        k["Latitude"] = soup.find(
            "section",
            {
                "id": "LocalFooter",
                "class": "footer",
                "itemtype": "http://schema.org/ProfessionalService",
            },
        ).find("meta", {"itemprop": "latitude", "content": True})["content"]
    except:
        k["Latitude"] = "<MISSING>"
    try:
        k["Longitude"] = soup.find(
            "section",
            {
                "id": "LocalFooter",
                "class": "footer",
                "itemtype": "http://schema.org/ProfessionalService",
            },
        ).find("meta", {"itemprop": "longitude", "content": True})["content"]
    except:
        k["Longitude"] = "<MISSING>"
    try:
        k["Address1"] = (
            soup.find(
                "address",
                {
                    "class": True,
                    "itemprop": "address",
                    "itemtype": "http://schema.org/PostalAddress",
                },
            )
            .find("span", {"itemprop": "streetAddress"})
            .text.replace("\t", "")
            .replace("\r", "")
            .replace("\n", "")
        )
    except:
        k["Address1"] = "<MISSING>"
    try:
        k["City"] = (
            soup.find(
                "address",
                {
                    "class": True,
                    "itemprop": "address",
                    "itemtype": "http://schema.org/PostalAddress",
                },
            )
            .find("span", {"itemprop": "addressLocality"})
            .text.replace(",", "")
        )
    except:
        k["City"] = "<MISSING>"
    try:
        k["State"] = (
            soup.find(
                "address",
                {
                    "class": True,
                    "itemprop": "address",
                    "itemtype": "http://schema.org/PostalAddress",
                },
            )
            .find("span", {"itemprop": "addressRegion"})
            .text
        )
    except:
        k["State"] = "<MISSING>"
    try:
        k["Zip"] = (
            soup.find(
                "address",
                {
                    "class": True,
                    "itemprop": "address",
                    "itemtype": "http://schema.org/PostalAddress",
                },
            )
            .find("span", {"itemprop": "postalCode"})
            .text
        )
    except:
        k["Zip"] = "<MISSING>"
    try:
        k["Phone"] = (
            soup.find(
                "section",
                {
                    "id": "LocalFooter",
                    "class": "footer",
                    "itemtype": "http://schema.org/ProfessionalService",
                },
            )
            .find("span", {"itemprop": "telephone"})
            .text.replace('"', "")
            .replace("\n", "")
        )
    except:
        k["Phone"] = "<MISSING>"
    hours = []
    try:
        hr = soup.find("ul", {"class": lambda x: x and "hours" in x})
        for i in hr.find_all("li", {"class": "flex", "data-item": True}):
            hours.append(
                str(i.find("strong").text)
                + ": "
                + i.text.replace(" ", "")
                .replace("\n", "")
                .replace('"', "")
                .replace("\t", "")
                .replace("\r", "")
            )
        k["PharmacyHoursForWeek"] = "; ".join(hours)
    except:
        k["PharmacyHoursForWeek"] = "<MISSING>"
    try:
        k["Type"] = soup.find(
            "section",
            {
                "id": "LocalFooter",
                "class": "footer",
                "itemtype": "http://schema.org/ProfessionalService",
            },
        ).find("meta", {"itemprop": "BranchOf", "content": True})["content"]
    except:
        k["Type"] = "<MISSING>"
    yield k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="merrymaids")
    url = "https://www.merrymaids.com/locations/"
    soup = ""
    with SgChrome() as driver:
        driver.get(url)
        items = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="LocationList"]/div/ul')
            )
        )
        time.sleep(60)
        soup = BeautifulSoup(driver.page_source, "lxml")
    links = soup.find_all(
        "a", {"class": "btn", "href": lambda x: x and x.endswith("?L=true")}
    )
    linkz = []
    for i in links:
        if i.text == "View Website":
            linkz.append(i["href"])
    dood = utils.parallelize(
        search_space=linkz,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )
    k = {}
    for i in dood:
        for j in i:
            k = j
            yield k
    items = "Finished grabbing data!!"
    logzilla.info(f"{items}")


def scrape():
    url = "https://merrymaids.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(
            mapping=["StoreDetailsPageUrl"],
            value_transform=lambda x: "https://merrymaids.com" + x,
            part_of_record_identity=True,
        ),
        location_name=MappingField(mapping=["Landmark"]),
        latitude=MappingField(mapping=["Latitude"]),
        longitude=MappingField(mapping=["Longitude"]),
        street_address=MappingField(mapping=["Address1"]),
        city=MappingField(mapping=["City"]),
        state=MappingField(mapping=["State"]),
        zipcode=MappingField(mapping=["Zip"]),
        country_code=MissingField(),
        phone=MappingField(mapping=["Phone"]),
        store_number=MissingField(),
        hours_of_operation=MappingField(
            mapping=["PharmacyHoursForWeek"], is_required=False
        ),
        location_type=MappingField(mapping=["Type"]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="merrymaids.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
