from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup
import ssl
import os

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-ca:{}@proxy.apify.com:8000/"

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("silvercar")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.silvercar.com"
base_url = "https://www.silvercar.com/car-rentals/"


def fetch_data():
    with SgRequests() as session:
        with SgChrome() as driver:
            driver.get(base_url)
            locations = bs(driver.page_source, "lxml").select(
                "div.locations-list div.location-detail a"
            )
            for link in locations:
                page_url = link["href"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                addr = link.select_one("span.address").text.strip().split(",")
                _p = sp1.find("h3", string=re.compile(r"^Phone$"))
                phone = ""
                if _p and _p.find_next_sibling():
                    phone = _p.find_next_sibling().text.strip()
                hours = []
                _hr = sp1.find("h3", string=re.compile(r"^Hours$"))
                if _hr:
                    hours = list(_hr.find_next_sibling().stripped_strings)
                yield SgRecord(
                    page_url=page_url,
                    location_name=link.select_one("span.name").text.strip(),
                    street_address=addr[0],
                    city=addr[1].strip(),
                    state=addr[-1].strip().split()[0].strip(),
                    zip_postal=addr[-1].strip().split()[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=", ".join(addr),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
