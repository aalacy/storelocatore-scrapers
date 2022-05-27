from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://tfc.com.ng/"
base_url = "https://tfc.com.ng/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul#menu-main-menu > li")[1].select("ul > li")
        for _ in locations:
            page_url = _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            block = [aa.text for aa in sp1.select("span.mad-icon-list-text")]
            raw_address = block[0]
            addr = parse_address_intl(raw_address + ", Nigeria")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            state = addr.state
            if not state and "Lagos" in raw_address:
                state = "Lagos"
            if state:
                state = state.replace(".", "")
            yield SgRecord(
                page_url=page_url,
                location_name=_.text.strip(),
                street_address=street_address.split("Festac")[0].strip(),
                city=_.text.strip(),
                state=state,
                zip_postal=addr.postcode,
                country_code="Nigeria",
                phone=block[-1].split(",")[0],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
