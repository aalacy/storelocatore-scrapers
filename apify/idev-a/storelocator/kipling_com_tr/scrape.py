from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kipling")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kipling.com.tr"
base_url = "https://www.kipling.com.tr/pages/magazalarimiz"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul.store-locator-item-list li")
        for _ in locations:
            addr = list(_.select_one("p.address").stripped_strings)
            yield SgRecord(
                page_url=base_url,
                location_name="Kipling",
                street_address=addr[0],
                city=_["data-city"],
                state=_["data-county"],
                country_code="Turkey",
                phone=_.select_one("p.phone a").text.strip(),
                latitude=_["data-latitude"],
                longitude=_["data-longitude"],
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
                hours_of_operation=_.select_one("p.working-hours").text.strip(),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
