from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import ssl
import re

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("veggiegrill")


locator_domain = "https://veggiegrill.com/"
base_url = "https://veggiegrill.com/locations/"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        locations = bs(driver.page_source, "lxml").select("div.accordions .location-sm")
        for location in locations:
            addr = list(location.select_one("address").stripped_strings)
            phone = location.find("a", href=re.compile("tel:")).text.strip()
            street_address = (
                " ".join(addr[:-1])
                .replace("Ackerman Student Union", "")
                .replace("New York, NY 10007", "")
                .strip()
            )
            if street_address.endswith(","):
                street_address = street_address[:-1]
            city = addr[-1].split(",")[0].strip()
            if city == "New Yor":
                city = "New York"
            yield SgRecord(
                page_url=base_url,
                store_number=location["id"],
                location_name=location.b.text.strip(),
                street_address=street_address,
                city=city,
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=" ".join(addr).replace("Ackerman Student Union", ""),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
