from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("moonvalleynurseries")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.moonvalleynurseries.com/"
base_url = "https://www.moonvalleynurseries.com/locations"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        tabs = soup.select("div#maintabContent div.tab-pane")
        for tab in tabs:
            locations = tab.select("div.subcontent-bg")
            for _ in locations:
                location_name = _.h6.text.strip()
                if "opening" in location_name.lower():
                    continue
                location_type = ""
                if "Moon Valley Nurseries" in location_name:
                    location_type = "Moon Valley Nursery"
                if "farm" in tab.h3.text.lower():
                    location_type = "Farm"
                page_url = locator_domain + _.a["href"]
                temp = []
                for pp in _.select("p"):
                    if pp.a:
                        break
                    raw = " ".join(pp.stripped_strings)
                    if not raw or "Contact" in raw:
                        continue
                    if "BY APPOINTMENT ONLY" in raw:
                        continue
                    temp.append(raw)

                raw_address = " ".join(temp)
                if not raw_address:
                    continue
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                if "Contact" in raw_address:
                    street_address = city = ""
                else:
                    street_address = street_address
                    city = addr.city
                phone = ""
                if _.select_one("p a.text-danger"):
                    phone = _.select_one("p a.text-danger").text.strip()
                yield SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    location_type=location_type,
                    phone=phone,
                    locator_domain=locator_domain,
                    raw_address=raw_address.replace("\n", " "),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LOCATION_TYPE,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
