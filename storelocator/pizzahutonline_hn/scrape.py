from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("kuwait")


locator_domain = "https://www.kuwait.kfc.me"
base_url = "https://www.google.hn/maps/ms?msa=0&msid=209883531638926848398.0004cfa94fd04bc5f56a7&hl=es&ie=UTF8&t=m&ll=15.518859,-88.019371&spn=0.078566,0.172348&z=13&output=embed"
map_url = "https://www.google.com/maps/dir//{},{}/@{},{}z"


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    }


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as session:
            res = session.get(base_url, headers=_headers())
            cleaned = (
                res.text.replace("\\\\u003d", "=")
                .replace("\\\\u0026", "&")
                .replace('\\"', '"')
                .replace("\xa0", " ")
            )
            locations = json.loads(
                cleaned.split('var _pageData = "')[1].split('";</script>')[0]
            )
            for _ in locations[1][6][0][12][0][13][0]:
                location_name = _[5][0][1][0].replace("\\n", "")
                latitude = _[1][0][0][0]
                longitude = _[1][0][0][1]
                logger.info(map_url.format(latitude, longitude, latitude, longitude))
                driver.get(map_url.format(latitude, longitude, latitude, longitude))
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//input[@class='tactile-searchbox-input']",
                        )
                    )
                )
                sp1 = bs(driver.page_source, "lxml")
                raw_address = (
                    sp1.select("input.tactile-searchbox-input")[-1]["aria-label"]
                    .replace("Destination", "")
                    .strip()
                )
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += ", " + addr.street_address_2
                yield SgRecord(
                    location_name=location_name,
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="Honduras",
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
