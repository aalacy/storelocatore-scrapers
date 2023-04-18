from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sgselenium import SgChrome
import json
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("lafaiveoil")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "http://www.lafaiveoil.com/"
base_url = "https://www.google.com/maps/d/embed?mid=18SGgyg9wkGAsTBGX2Wq8QFMYs4zKye7s&wmode=opaque"
map_url = "https://www.google.com/maps/dir//{},{}/@{},{}z"


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as session:
            sp0 = bs(session.get(locator_domain, headers=_headers).text, "lxml")
            _hr = sp0.find("", string=re.compile(r"^Hours of Operation"))
            hours = []
            if _hr:
                hours = list(_hr.find_parent("p").stripped_strings)[1:]
            res = session.get(base_url, headers=_headers)
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
                    page_url="https://www.lafaiveoil.com/locations/",
                    location_name=location_name,
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
