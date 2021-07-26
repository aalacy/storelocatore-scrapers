from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
import time
import json
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("kungfutea")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kungfutea.com"
base_url = "https://www.kungfutea.com/locations/usa"
json_url = "https://api.storepoint.co/v1/"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select('div[data-controller-folder="locations"] a')
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            driver.get(page_url)
            logger.info(page_url)
            exist = False
            while not exist:
                time.sleep(1)
                for rr in driver.requests[::-1]:
                    if rr.url.startswith(json_url) and rr.response:
                        exist = True
                        locations = json.loads(rr.response.body)["results"]["locations"]
                        for _ in locations:
                            addr = parse_address_intl(_["streetaddress"])
                            street_address = addr.street_address_1
                            if addr.street_address_2:
                                street_address += " " + addr.street_address_2
                            if _["monday"] == "":
                                hours_of_operation = "<MISSING>"
                            else:
                                hours_of_operation = (
                                    "Monday: "
                                    + _["monday"]
                                    + ", "
                                    + "Tuesday: "
                                    + _["tuesday"]
                                    + ", "
                                    + "Wednesday: "
                                    + _["wednesday"]
                                    + ", "
                                    + "Thursday: "
                                    + _["thursday"]
                                    + ", "
                                    + "Friday: "
                                    + _["friday"]
                                    + ", "
                                    + "Saturday: "
                                    + _["saturday"]
                                    + ", "
                                    + "Sunday: "
                                    + _["sunday"]
                                )

                            if "coming soon" in _["name"].lower():
                                continue
                            location_type = ""
                            if "temporarily closed" in _["name"].lower():
                                location_type = "temporarily closed"
                            yield SgRecord(
                                page_url=page_url,
                                store_number=_["id"],
                                location_name=_["name"],
                                street_address=street_address,
                                city=addr.city,
                                state=addr.state,
                                zip_postal=addr.postcode,
                                country_code=link.text.strip(),
                                phone=_["phone"],
                                location_type=location_type,
                                locator_domain=locator_domain,
                                latitude=_["loc_lat"],
                                longitude=_["loc_long"],
                                hours_of_operation=hours_of_operation.replace(
                                    ",", ";"
                                ).replace("–", "-"),
                            )

                        break


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
