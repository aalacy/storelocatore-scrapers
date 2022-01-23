from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgselenium import SgChrome
import re
from sgscrape.sgrecord_id import SgRecordID
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


logger = SgLogSetup().get_logger("servisfirstbank")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.servisfirstbank.com"
    base_url = "https://www.servisfirstbank.com/locations/"
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("div#locations_squares > a")
        logger.info(f"{len(links)} states found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            driver.get(page_url)
            sp1 = bs(driver.page_source, "lxml")
            locations = sp1.select("div#location_spots > div.main_spot")
            locations += sp1.select("div#location_spots > div.other_spots div.spot")
            for _ in locations:
                if not _.text.strip():
                    continue
                addr = list(_.select_one(".spot_text").stripped_strings)
                _hr = _.find("div", string=re.compile(r"Lobby Hours"))
                hours_of_operation = ""
                if _hr:
                    hours_of_operation = " ".join(
                        list(_hr.find_next_sibling().stripped_strings)
                    )
                location_type = "branch"
                if _.select_one('img[alt="atm icon"]'):
                    location_type += ",atm"
                phone = ""
                if _.find("a", href=re.compile(r"tel:")):
                    phone = _.find("a", href=re.compile(r"tel:")).text.strip()
                yield SgRecord(
                    page_url=page_url,
                    location_name=_.select_one("div.spot_title").text.strip(),
                    street_address=" ".join(addr[:-1]),
                    city=addr[-1].split(",")[0].strip(),
                    state=" ".join(addr[-1].split(",")[1].strip().split(" ")[:-1]),
                    zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    location_type=location_type,
                    hours_of_operation=hours_of_operation.replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
