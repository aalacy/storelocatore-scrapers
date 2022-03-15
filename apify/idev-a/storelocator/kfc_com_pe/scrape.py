from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kfc")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://kfc.com.pe"
base_url = "https://kfc.com.pe/find-a-kfc"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.customAccordionStoreList div.card")
        for _ in locations:
            trs = [tr for tr in _.select("table tr") if tr.text.strip()]
            _addr = list(trs[0].stripped_strings)
            addr = parse_address_intl(" ".join(_addr) + ", Peru")
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_.select_one("h5 a").text.strip(),
                street_address=_addr[0],
                city=addr.city,
                state=addr.state,
                country_code="Peru",
                locator_domain=locator_domain,
                hours_of_operation=": ".join(trs[1].stripped_strings),
                raw_address=" ".join(_addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
