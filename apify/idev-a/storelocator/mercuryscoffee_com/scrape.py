from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("mercurys")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.mercurys.com"
base_url = "https://www.mercurys.com/pages/locations-1"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locs = [
            _
            for _ in soup.select("div.item-content div.element-wrap")
            if _["data-label"] != "Button" and _["data-label"] != "Image"
        ]
        for x in range(0, len(locs), 2):
            block = list(locs[x + 1].stripped_strings)
            raw_address = None
            for y, bb in enumerate(block):
                if bb.startswith("(") and bb.endswith(")") or bb == "TAKE A TOUR":
                    del block[y]

            hours = []
            for y, bb in enumerate(block):
                if bb.startswith("MON") or bb.startswith("SUN"):
                    raw_address = " ".join(block[:y])
                    hours = block[y:-1]
                    break
            if not raw_address:
                raw_address = block[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            location_name = locs[x].h1.text.strip()
            logger.info(location_name)
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=block[-1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
