from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
import json
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("bricktops")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://bricktops.com"
base_url = "https://bricktops.com/locations"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("div.sqs-gallery a")
        for link in links:
            page_url = link["href"] + "/contact"
            if not link["href"].startswith("http"):
                page_url = locator_domain + link["href"]
            logger.info(page_url)
            driver.get(page_url)
            sp1 = bs(driver.page_source, "lxml")
            addr = None
            hours_of_operation = ""
            phone = ""
            latitude = longitude = ""
            if sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
            if not link["href"].startswith("https"):
                location_name = sp1.select_one(".sqs-block-content h1").text
                hours_of_operation = "; ".join(
                    [
                        _.text
                        for _ in sp1.select("div.sqs-block-html div.sqs-block-content")[
                            -1
                        ].select("p")[1:-1]
                    ]
                ).replace("–", "-")
                ss = json.loads(sp1.select_one("div.map-block")["data-block-json"])[
                    "location"
                ]
                latitude = ss["mapLat"]
                longitude = ss["mapLng"]
                addr = []
                addr.append(ss["addressLine1"])
                addr.append(ss["addressLine2"])
            else:
                addr = list(
                    sp1.select("div.sqs-block-html div.sqs-block-content")[0]
                    .select("p")[-1]
                    .stripped_strings
                )
                location_name = link.img["alt"].replace(".png", "")
            street_address = addr[0]
            raw_address = " ".join(addr)
            addr = parse_address_intl(raw_address)
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                phone=phone,
                country_code="US",
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
