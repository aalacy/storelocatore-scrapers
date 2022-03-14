from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.electricbase.co.uk"
base_url = "https://www.electricbase.co.uk/storefinder"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("storeLocator.initialize(")[1]
            .split(", false)")[0]
        )["all"]
        for _ in locations:

            page_url = f"https://www.electricbase.co.uk/storefinder/store/{_['Address3']}-{_['ID']}"
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _hr = sp1.find("", string=re.compile(r"Opening Times"))
            hours = []
            if _hr:
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in _hr.find_parent("h3").find_next_sibling("ul").select("li")
                ]
            _addr = list(sp1.address.stripped_strings)
            addr = parse_address_intl(", ".join(_addr[:-1]) + ", United Kingdom")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=page_url,
                store_number=_["ID"],
                location_name=_["LocationName"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=_["postcode"],
                latitude=_["Lat"],
                longitude=_["Lng"],
                country_code="UK",
                phone=_["Phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(_addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.CITY,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
