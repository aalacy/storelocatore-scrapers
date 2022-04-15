import time
import json
import ssl
from sgselenium.sgselenium import SgChrome
from selenium.webdriver.common.by import By
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

ssl._create_default_https_context = ssl._create_unverified_context

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

DOMAIN = "motionindustries.com"

logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
start_urls = "https://www.motioncanada.ca/misvc/mc/services/json/locations.locations"


def fetch_data():
    all_poi = []
    logger.info("Initiating Chrome Driver")
    with SgChrome(user_agent=user_agent) as driver:

        driver.get(start_urls)
        logger.info("Loading Targer Page")
        data = json.loads(driver.find_element(By.CSS_SELECTOR, "body").text)
        all_poi += data["rows"]

        for poi in all_poi:
            page_url = "<MISSING>"
            location_name = poi["label"]
            street_address = poi["addrLine2"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi["state"]
            state = state if state else "<MISSING>"
            zip_code = poi["zip"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["country"]
            if country_code == "Canada":
                country_code = "CA"
            elif country_code == "Mexico":
                country_code = "MX"
            else:
                country_code = "US"

            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["miLoc"]
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"

            if poi["isShop"] is True:
                location_type = "Motion Shop"
            else:
                location_type = "Motion Branch"

            latitude = poi["latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = []
            for elem in poi["openCloseTimes"]:
                if elem["closeTime"] == "Closed":
                    hours_of_operation.append("{} closed".format(elem["dayOfWeek"]))
                elif not elem["openTime"]:
                    hours_of_operation.append("{} closed".format(elem["dayOfWeek"]))
                else:
                    hours_of_operation.append(
                        "{} {} - {}".format(
                            elem["dayOfWeek"], elem["openTime"], elem["closeTime"]
                        )
                    )
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

            yield SgRecord(
                locator_domain=DOMAIN,
                store_number=store_number,
                page_url=page_url,
                location_name=location_name,
                location_type=location_type,
                street_address=street_address,
                city=city,
                zip_postal=zip_code,
                state=state,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ...")
    start = time.time()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    logger.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
