from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mercurys")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.mercurys.com/pages/locations-1"
    base_url = "https://www.mercurys.com/pages/locations-1"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        try:
            locs = [
                _
                for _ in soup.select("div.item-content div.element-wrap")
                if _["data-label"] != "Button" and _["data-label"] != "Image"
            ]
        except:
            import pdb

            pdb.set_trace()
        for x in range(0, len(locs), 2):
            block = list(locs[x + 1].stripped_strings)
            address = None
            for y, bb in enumerate(block):
                if bb.startswith("(") and bb.endswith(")") or bb == "TAKE A TOUR":
                    del block[y]

            for y, bb in enumerate(block):
                if bb.startswith("MON"):
                    address = " ".join(block[:y])
                    hours = block[y:-1]
                    break
            addr = parse_address_intl(address)
            location_name = locs[x].h1.text.strip()
            logger.info(location_name)
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=block[-1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
