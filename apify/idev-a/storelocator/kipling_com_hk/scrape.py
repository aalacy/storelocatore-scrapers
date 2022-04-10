from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("kipling")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kipling.com.hk"
base_url = "https://www.kipling.com.hk/en/kipling-stores/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("li.address-item")
        for _ in locations:
            raw_address = _.select_one("div.address").text.strip()
            if not raw_address:
                continue
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = (
                _.find("div", string=re.compile(r"PHONE"))
                .find_next_sibling()
                .text.strip()
            )
            hours = "; ".join(
                _.find("div", string=re.compile(r"OPENING HOUR"))
                .find_next_sibling()
                .stripped_strings
            )
            name = _.select_one("div.name").text.strip()
            location_name = "Kipling"
            if "Outlet" in name:
                location_name = "Kipling Outlet"
            yield SgRecord(
                page_url=base_url,
                store_number=_["data-id"],
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Hong Kong",
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours.replace("\n", "; "),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
